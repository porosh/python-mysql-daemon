import os
import asyncio
import aiohttp
import aiosmtplib
import aiomysql
import boto3
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import random

# Load environment variables from .env file
load_dotenv()

# Ensure the logs directory exists
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

# Configuration for notifications
SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = int(os.getenv('SMTP_PORT'))
SMTP_USERNAME = os.getenv('SMTP_USERNAME')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')

AWS_REGION = os.getenv('AWS_REGION')

DB_CONFIG = {
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'db': os.getenv('DB_NAME'),
    'host': os.getenv('DB_HOST'),
    'port': int(os.getenv('DB_PORT')),
}

CHUNK_SIZE = 500
PROC_NAME = 'worker_1'  # Example processor name, you can make this dynamic

# Initialize AWS SNS and SES clients
sns_client = boto3.client('sns', region_name=AWS_REGION)
ses_client = boto3.client('ses', region_name=AWS_REGION)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"{log_dir}/daemon.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def main():
    while True:
        try:
            await process_clients()
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            print(f"Error in main loop: {e}")
        await asyncio.sleep(random.randint(1, 7))

async def process_clients():
    logger.info("Processing clients")
    print("Processing clients")
    pool = await aiomysql.create_pool(**DB_CONFIG)
    try:
        clients = await get_clients(pool, CHUNK_SIZE)
        tasks = [send_notifications(client, pool) for client in clients]
        await asyncio.gather(*tasks)
    except Exception as e:
        logger.error(f"Error in process_clients: {e}")
        print(f"Error in process_clients: {e}")
    finally:
        pool.close()
        await pool.wait_closed()

async def get_clients(pool, limit):
    logger.info(f"Fetching up to {limit} clients with status 'pending'")
    print(f"Fetching up to {limit} clients with status 'pending'")
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute('SELECT * FROM clients WHERE status = %s LIMIT %s FOR UPDATE', ('pending', limit))
            result = await cursor.fetchall()
            if result:
                client_ids = [client['id'] for client in result]
                await cursor.execute('UPDATE clients SET status = %s, proc_name = %s WHERE id IN (%s)', 
                                     ('processing', PROC_NAME, ','.join(map(str, client_ids))))
                await conn.commit()
            logger.info(f"Fetched {len(result)} clients")
            print(f"Fetched {len(result)} clients")
            return result

async def send_notifications(client, pool):
    logger.info(f"Sending notifications to client {client['id']}")
    print(f"Sending notifications to client {client['id']}")
    push_status = 'no'
    email_status = 'no'
    try:
        tasks = [
            send_push_notification(client),
            send_email(client)
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        if isinstance(results[0], Exception):
            push_status = 'no'
        else:
            push_status = 'yes'
        
        if isinstance(results[1], Exception):
            email_status = 'no'
        else:
            email_status = 'yes'
        
        await update_client_status(pool, client['id'], 'notified', push_status, email_status)
    except Exception as e:
        logger.error(f"Error sending notifications to client {client['id']}: {e}")
        print(f"Error sending notifications to client {client['id']}: {e}")
        await update_client_status(pool, client['id'], 'error', push_status, email_status)

async def send_push_notification(client):
    logger.info(f"Sending push notification to {client['push_id']}")
    print(f"Sending push notification to {client['push_id']}")
    try:
        # response = sns_client.publish(
        #     TargetArn=client['push_id'],
        #     Message='Notification Body',
        #     Subject='Notification Title'
        # )
        asyncio.sleep(random.randint(1, 3))
        logger.info(f"Push notification sent to {client['push_id']}")
        print(f"Push notification sent to {client['push_id']}")
    except Exception as e:
        logger.error(f"Failed to send push notification to {client['push_id']}: {e}")
        print(f"Failed to send push notification to {client['push_id']}: {e}")
        raise

async def send_email(client):
    logger.info(f"Sending email to {client['email']}")
    print(f"Sending email to {client['email']}")
    msg = MIMEMultipart()
    msg['From'] = SMTP_USERNAME
    msg['To'] = client['email']
    msg['Subject'] = 'Notification Subject'

    body = 'Notification Body'
    msg.attach(MIMEText(body, 'plain'))

    try:
        # response = ses_client.send_raw_email(
        #     Source=SMTP_USERNAME,
        #     Destinations=[client['email']],
        #     RawMessage={
        #         'Data': msg.as_string()
        #     }
        # )
        asyncio.sleep(random.randint(1, 3))
        logger.info(f"Email sent to {client['email']}")
        print(f"Email sent to {client['email']}")
    except Exception as e:
        logger.error(f"Failed to send email to {client['email']}: {e}")
        print(f"Failed to send email to {client['email']}: {e}")
        raise

async def update_client_status(pool, client_id, status, is_push_sent, is_email_sent):
    logger.info(f"Updating status of client {client_id} to {status}")
    print(f"Updating status of client {client_id} to {status}")
    try:
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                # await cursor.execute(
                #     'UPDATE clients SET status = %s, is_push_sent = %s, is_email_sent = %s WHERE id = %s', 
                #     (status, is_push_sent, is_email_sent, client_id)
                # )
                # await conn.commit()
                asyncio.sleep(random.randint(1, 3))
                logger.info(f"Updated status of client {client_id} to {status}")
                print(f"Updated status of client {client_id} to {status}")
    except Exception as e:
        logger.error(f"Failed to update status of client {client_id}: {e}")
        print(f"Failed to update status of client {client_id}: {e}")

if __name__ == "__main__":
    asyncio.run(main())