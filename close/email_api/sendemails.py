import logging
import math
import sqlite3
import time
from sqlite3 import Error as sqliteError
from datetime import date
import json
import logging
import time
from datetime import date

import requests
from closeio_api import Client
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# your close api secret key & api urls
CLOSE_API_KEY = 'api_6UOHiS0CDzQtMWeUePrqfX.6dMY8E1N4Nzu3i3olfEDPE'
USER_ID = 'user_l0UqCXVwEd82vSOui1HxhVAyTAf0hOa9BDxsXizfJhV'
EMAIL_TEMPLATE_ID = 'tmpl_6i4qWyPodtm0pfpJPR19W58EL9LfzNSJfKaPsH98en2'
SQLITE_DB_PATH = 'client_sqlite.db'
EMAIL_SUBJECT = 'Quick question'
PER_DAY_SENT_MAX_LIMIT = 30  # Emails
WAITING_TIME_BETWEEN_TWO_CONSECUTIVE_EMAILS = 16  # minutes
EMAIL_TRACER_BASE_URL = 'https://4cfa-2a09-bac1-b00-8-00-13-2c9.ngrok-free.app'
EMAIL_TRACER_FAKE_IMG_API_URL = EMAIL_TRACER_BASE_URL + '/email/api/pixel'

# log format
logging.basicConfig(
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%H:%M:%S',
    level=logging.INFO)


def send_message_to_slack(text, color='good'):
    # update this to your slack webhook
    SLACK_WEBHOOK = 'https://hooks.slack.com/services/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'

    data = json.dumps({
        "attachments": [
            {
                "color": color,
                "text": text
            }
        ]
    })
    response = requests.post(SLACK_WEBHOOK, data=data)

    if response.status_code != 200:
        raise ValueError(
            f'Request to slack returned an error {response.status_code}, the response is:\n{response.text}')


def create_tables(conn):
    _leads_table = """ CREATE TABLE IF NOT EXISTS leads (
                                                    id integer PRIMARY KEY,
                                                    lead_id text NOT NULL,
                                                    date_time text NOT NULL
                                                ); """
    _contacts_table = """ CREATE TABLE IF NOT EXISTS contacts (
                                                        id integer PRIMARY KEY,
                                                        lead_ref_id text NOT NULL,
                                                        first_name text,
                                                        last_name text,
                                                        company_name text,
                                                        url text,
                                                        individual_li_url text,
                                                        company_li_url text,
                                                        email text,
                                                        phone text,
                                                        industry text,
                                                        title text,
                                                        seniority text,
                                                        num_employees text,
                                                        first_email_send boolean,
                                                        date_time text NOT NULL
                                                    ); """
    _email_table = """ CREATE TABLE IF NOT EXISTS emails (
                                                id integer PRIMARY KEY,
                                                sender_email text NOT NULL,
                                                receiver_email text NOT NULL,
                                                send_via_close boolean NOT NULL,
                                                sending_date text NOT NULL,
                                                email_template text,
                                                reply_to text,
                                                email_opened boolean,
                                                opened_counter int DEFAULT 0,
                                                last_opened_at text,
                                                lead_replied boolean,
                                                lead_replied_at text
                                            ); """
    _connected_accounts_table = """ CREATE TABLE IF NOT EXISTS connected_accounts (
                                                    id integer PRIMARY KEY,
                                                    account_name text NOT NULL,
                                                    account_email text NOT NULL,
                                                    account_password text,
                                                    send_via_close boolean NOT NULL,
                                                    reply_to text,
                                                    account_email_id text NOT NULL
                                                ); """
    try:
        c = conn.cursor()
        c.execute(_contacts_table)
        c.execute(_leads_table)
        c.execute(_email_table)
        c.execute(_connected_accounts_table)
    except sqliteError as ex:
        logging.error('error while creating table', ex)


def create_db_connection(db_file):
    try:
        conn = sqlite3.connect(db_file)
    except sqliteError as ex:
        logging.error(ex)
        exit()
    return conn


def create_email_sent_confirmation(conn, sender_email, receiver_email, send_via_close, sending_date, email_template, reply_to):
    sql = f"""INSERT INTO emails (sender_email, receiver_email, send_via_close, sending_date, email_template, reply_to) VALUES ('{sender_email}','{receiver_email}', '{send_via_close}', '{sending_date}', '{email_template}', '{reply_to}')"""
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()


def make_email_payload(contact_id, receiver_email, lead_id, email_account_id):
    return {
        "email_account_id": email_account_id,
        "contact_id": contact_id,
        "user_id": USER_ID,
        "lead_id": lead_id,
        "direction": "outgoing",
        "to": [receiver_email],
        "bcc": [],
        "cc": [],
        "status": "outbox",
        "attachments": [],
        "template_id": EMAIL_TEMPLATE_ID,
    }


def send_email_via_close(api, payload):
    res_data = api.post('activity/email', payload)
    if res_data.get('id') not in ['', None]:
        return True

    # handle rate limit
    if res_data.get('error'):
        if res_data.get('error').get('rate_reset'):
            rate_reset = math.ceil(res_data.get('error').get('rate_reset')) + 1
            logging.info(
                f"{res_data.get('error').get('message')}, wait for {rate_reset}s")
            time.sleep(rate_reset)
    return False


def send_email_via_google(sender_email, sender_pass, receiver_email, receiver_name, reply_to: str) -> str:
    try:

        # set up the SMTP server connection
        smtp_server = 'smtp.gmail.com'
        smtp_port = 587
        smtp_username = sender_email
        # need to generate app password, your regular gmail pass won't work
        smtp_password = sender_pass
        smtp_connection = smtplib.SMTP(smtp_server, smtp_port)
        smtp_connection.starttls()
        smtp_connection.login(smtp_username, smtp_password)

        # set up the email message
        body = f"""<p dir=\"ltr\" id=\"isPasted\">Hi {receiver_name.split(' ')[0]},</p><div color=\"rgb(75, 81, 93)\"><br>I'm curious if you've 
                    considered outsourcing your customer support?&nbsp;<br><br>I know that can be a scary thought–but we do things 
                    differently than you might have heard about or experienced.</div><div color=\"rgb(75, 81, 93)\"><br></div><div 
                    color=\"rgb(75, 81, 93)\">My name is Jim, and I'm the Co-Founder of xFusion. We offer a fully-managed customer 
                    support solution with a unique approach that combines human expertise and AI technology.</div>We're convinced 
                    that the foundation of outstanding customer support lies in having a valued and inspired team. We prioritize 
                    investing in our agents by providing attractive compensation and creating an enjoyable, supportive work 
                    atmosphere, which in turn generates top-notch service for our clients and their customers.<br><br>Because we 
                    empower our agents with the latest AI tools like ChatGPT and Intercom Fin, they\\'re up to 3x more productive 
                    than traditional customer support reps. This combination of technology and talent sets us 
                    apart.&nbsp;<br><br>Lastly, we understand the importance of trust when it comes to outsourcing, and we believe 
                    it\\'s our responsibility to earn your business. Therefore, no upfront payment is required. If you’re not happy 
                    after 30 days, you can walk and not pay a dime.<br><br>If you think having a short conversation makes sense, 
                    please let me know.<br><br>Thank you for taking the time to read this, {receiver_name.split(' ')[0]}!<br><div color=\"rgb(75, 81, 
                    93)\">&nbsp;</div><div color=\"rgb(75, 81, 93)\">Jim - Co-Founder of <a fr-original-style=\"user-select: auto;\" 
                    href=\"http://xfusion.io/\" rel=\"noopener noreferrer noopener\" style=\"user-select: 
                    auto;\">xFusion.io</a></div><div color=\"rgb(75, 81, 93)\" data-en-clipboard=\"true\" data-pm-slice=\"1 1 []\">(
                    If you want me gone like a bad haircut, let me know and I\'ll disappear faster than a toupee in a 
                    hurricane)<img src="{EMAIL_TRACER_FAKE_IMG_API_URL}?e={receiver_email}"  alt=""/></div>"""
        html = f"""
        <html>
          <head></head>
          <body>
                {body}
          </body>
        </html>
        """

        raw_template = f"Hi {receiver_name.split(' ')[0]}, I am curious if you have considered outsourcing your customer" \
                       f" support? I know that can be a scary thought–but we do things differently than you might have" \
                       f" heard about or experienced. My name is Jim, and I am the Co-Founder of xFusion. We offer a " \
                       f"fully-managed customer support solution with a unique approach that combines human expertise " \
                       f"and AI technology. We are convinced that the foundation of outstanding customer support lies in" \
                       f" having a valued and inspired team. We prioritize investing in our agents by providing" \
                       f" attractive compensation and creating an enjoyable, supportive work atmosphere, which in turn " \
                       f"generates top-notch service for our clients and their customers. Because we empower our " \
                       f"agents with the latest AI tools like ChatGPT and Intercom Fin, they are up to 3x more productive " \
                       f"than traditional customer support reps. This combination of technology and talent sets us " \
                       f" apart. Lastly, we understand the importance of trust when it comes to" \
                       f" outsourcing, and we believe it is our responsibility to earn your business. Therefore, " \
                       f"no upfront payment is required. If you are not happy after 30 days, you can walk and not pay" \
                       f" a dime. If you think having a short conversation makes sense, please let me know. " \
                       f"Thank you for taking the time to read this, {receiver_name.split(' ')[0]}! Jim - Co-Founder" \
                       f" of xFusion.io. If you want me gone like a bad haircut, let me know and I'll disappear faster " \
                       f"than a toupee in a hurricane".replace("\'", '').replace("\"", '').strip()

        message = MIMEMultipart('alternative')
        message['From'] = sender_email
        message['To'] = receiver_email
        if reply_to:
            message['reply-to'] = reply_to
        message['Subject'] = EMAIL_SUBJECT
        html_part = MIMEText(html, 'html')
        message.attach(html_part)

        # send the email
        smtp_connection.sendmail(sender_email, receiver_email, message.as_string())

        # close the SMTP server connection
        smtp_connection.quit()
        return raw_template

    except Exception as ex:
        return ""


def get_contacts(conn):
    contacts = []

    lead_cursor = conn.execute("SELECT * FROM leads")
    leads = lead_cursor.fetchall()

    for lead in leads:
        try:
            contact_cursor = conn.execute(
                "SELECT * FROM contacts WHERE lead_ref_id=?", (lead[0],))
            contact = contact_cursor.fetchone()
            contact_first_name = contact[2]
            contact_email = contact[8]
            contacts.append([lead[1], contact_first_name, contact_email])
        except Exception:
            pass

    return contacts


def get_connected_accounts(conn):
    cursor = conn.execute("SELECT * FROM connected_accounts")
    return cursor.fetchall()


def check_email_already_send(conn, receiver_email) -> bool:
    cursor = conn.execute(
        "SELECT * FROM emails WHERE receiver_email=?", (receiver_email,))
    if len(cursor.fetchall()) == 0:
        return False
    return True


def check_lead_availability(conn, lead_id) -> bool:
    cursor = conn.execute("SELECT * FROM leads WHERE lead_id=?", (lead_id,))
    if len(cursor.fetchall()) == 0:
        return False
    return True


def assign_timestamp_with_limit(connected_accounts: list) -> dict:
    data = {}
    for connected_account in connected_accounts:
        data[connected_account[2]] = {'timestamp': time.time(), 'limit': 0}
    return data


def update_timestamp_with_limit(connected_accounts_time_limits, sender_email) -> dict:
    timestamp, limit = connected_accounts_time_limits[sender_email]['timestamp'], \
        connected_accounts_time_limits[sender_email]['limit']
    connected_accounts_time_limits[sender_email] = {
        'timestamp': time.time() + (WAITING_TIME_BETWEEN_TWO_CONSECUTIVE_EMAILS * 60), 'limit': limit + 1}
    return connected_accounts_time_limits


def check_any_connected_accounts_have_valid_limit(connected_accounts_time_limits) -> bool:
    for key in connected_accounts_time_limits:
        if connected_accounts_time_limits[key]['limit'] < PER_DAY_SENT_MAX_LIMIT:
            return True
    return False


def check_connected_account_availability(data: dict, connect_account_email: str) -> bool:
    try:
        if time.time() > data[connect_account_email]['timestamp'] \
                and data[connect_account_email]['limit'] <= PER_DAY_SENT_MAX_LIMIT:
            return True
        return False
    except Exception as ex:
        return False


def get_contact_id_from_lead_api(api, lead_id) -> str:
    try:
        res_data = api.get(f'/lead/{lead_id}')
        return res_data['contacts'][0]['id']
    except Exception as e:
        return ''


def add_activity_note(api, lead_id: str, note: str):
    api.post('activity/note', data={"note": note, "lead_id": lead_id})
    logging.info("note pushed to close")


def run():
    logging.info('SendEmails Script starts running ...')
    # send_message_to_slack('SendEmails Script has started running ...')

    # initialize db connection
    conn = create_db_connection(SQLITE_DB_PATH)

    # create tables
    create_tables(conn)

    # create close api instance
    api = Client(CLOSE_API_KEY)

    # fetch all the available contacts from close
    contacts = get_contacts(conn)

    # fetch all the available connected accounts from db
    connected_accounts = get_connected_accounts(conn)
    total_connected_accounts = len(connected_accounts)

    # assign timestamp & per execution sending limit to all the connected accounts
    connected_accounts_time_limits = assign_timestamp_with_limit(
        connected_accounts)

    # total number of contacts
    total_contacts = len(contacts)
    success_counter = 0

    # looping all the connected accounts to send email
    contacts_pointer = 0
    """ 
        The script will try to send an email to all the contacts, if the limit of connected accounts is exceeded then run it will run again the next day.
    """
    while contacts_pointer < total_contacts:

        # take a single contact to sent email
        while check_email_already_send(conn, contacts[contacts_pointer][2]) is True:
            contacts_pointer += 1
            if contacts_pointer >= total_contacts:
                break
            logging.info(
                f"{contacts[contacts_pointer][2]} already received an email, ignoring...")

        # exit the script if all the available contacts receive email
        if contacts_pointer == total_contacts:
            logging.info(
                'All contacts in the database have received emails. Exiting the script.')
            # send_message_to_slack(
            # 'All contacts in the database have received emails. Exiting the script.')
            exit()

        """ 
            1st email will be sent from 1st connected account, 2nd from 2nd connected account and so on. 
            If the list in the DB is short then the process will repeat from the first email index in the DB
        """
        connected_accounts_pointer = 0
        try:
            while connected_accounts_pointer < total_connected_accounts:
                contact = contacts[contacts_pointer]
                connected_account = connected_accounts[connected_accounts_pointer]

                # check whether the connected account is available to send email
                if check_connected_account_availability(connected_accounts_time_limits, connected_account[2]) is False:
                    logging.info(
                        f'{connected_account[2]} is not available to send emails now, ignoring...')
                    connected_accounts_pointer += 1
                    continue

                # extract required data.bson
                receiver_email = contact[2]
                receiver_name = contact[1]
                lead_id = contact[0]
                contact_id = get_contact_id_from_lead_api(api, lead_id)
                if contact_id == '':
                    logging.info(
                        f'Failed to get the contact id for `{lead_id}` this lead id, ignoring...')
                    contacts_pointer += 1
                    continue
                sender_email = connected_account[2]
                # required if email sent configured via Google
                sender_pass = connected_account[3]
                reply_to = connected_account[5]  # will use if not null
                email_account_id = connected_account[6]  # will use for close

                # make decision which service to use (close or gmail)
                # this connected account configured to send email via close
                if connected_account[4]:

                    # generate payload to send email
                    payload = make_email_payload(
                        contact_id, receiver_email, lead_id, email_account_id)

                    # send email via close
                    if send_email_via_close(api, payload) is True:
                        # create confirmation entry in email table
                        create_email_sent_confirmation(conn, sender_email, receiver_email, True,
                                                       date.today().strftime("%m/%d/%Y"), "", reply_to)

                        # update the timestamp & limit for the used connected account
                        connected_accounts_time_limits = update_timestamp_with_limit(connected_accounts_time_limits,
                                                                                     sender_email)

                        # increase contacts pointer & success counter
                        contacts_pointer += 1
                        connected_accounts_pointer += 1
                        success_counter += 1

                        logging.info(
                            f'--> Successfully sent email to {receiver_email} from {sender_email} via Close API')

                    else:
                        logging.info(
                            f'--> Failed to send email {receiver_email} from {sender_email} via Close API')

                else:  # this connected account configured to send email via Google

                    template = send_email_via_google(sender_email, sender_pass, receiver_email,
                                                     receiver_name, reply_to)

                    if template != "":
                        # create confirmation entry in email table
                        create_email_sent_confirmation(conn, sender_email, receiver_email, False,
                                                       date.today().strftime("%m/%d/%Y"), str(template), reply_to)

                        # update the timestamp & limit for the used connected account
                        connected_accounts_time_limits = update_timestamp_with_limit(connected_accounts_time_limits,
                                                                                     sender_email)

                        # add activity notes
                        add_activity_note(api, lead_id, template + f"\n sent from {sender_email}")

                        # increase contacts pointer & success counter
                        contacts_pointer += 1
                        connected_accounts_pointer += 1
                        success_counter += 1

                        logging.info(
                            f'--> Successfully sent email to {receiver_email} from {sender_email} via Gmail API')

                    else:
                        logging.info(f'--> Failed to send email {receiver_email} from {sender_email} via Gmail API')

        except Exception as e:
            print(e)
            pass

        # check whether all connected account reached their PER_DAY_SENT_LIMIT emails per day limit
        if check_any_connected_accounts_have_valid_limit(connected_accounts_time_limits) is False:
            break

        """ wait WAITING_BETWEEN_TWO_CONSECUTIVE_EMAIL minutes to reset connected accounts timestamp the process, 
            this will help the program to use all the available connected accounts under PER_DAY_SENT_LIMIT days limit.
        """
        logging.info(
            f'For resetting connected accounts timestamp waiting {WAITING_TIME_BETWEEN_TWO_CONSECUTIVE_EMAILS} minutes...')
        time.sleep(WAITING_TIME_BETWEEN_TWO_CONSECUTIVE_EMAILS * 60)

    logging.info(
        f'total {success_counter} emails have been sent via this script.')
    logging.info('Script execution completed successfully!')
    # send_message_to_slack(f'Script has executed successfully! Total {success_counter} emails have been sent via this script.')


if __name__ == '__main__':
    run()
