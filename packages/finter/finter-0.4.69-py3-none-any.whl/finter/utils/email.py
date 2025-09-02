import os
import base64
import mimetypes
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import email

import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

from finter.settings import logger


# 환경 변수에서 AWS 자격 증명 가져오기
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_REGION = os.environ.get('AWS_REGION', 'ap-northeast-2')  # 기본값 설정


def send_email(
        sender,  # Must be an email registered with Amazon SES.
        recipient,
        subject,
        body,  # 이메일 본문 내용
        cc_addresses=None,  # CC 수신자 리스트
        bcc_addresses=None,  # BCC 수신자 리스트
        attachments=None,  # 첨부 파일 경로 리스트
        addon_subject=None,
):
    """
    이메일을 전송합니다.
    Args:
        sender (str): 발신자 이메일
        recipient (str or list): 수신자 이메일 또는 이메일 리스트
        subject (str): 이메일 제목
        body (str): 이메일 본문
        cc_addresses (list, optional): CC 수신자 이메일 리스트
        bcc_addresses (list, optional): BCC 수신자 이메일 리스트
        attachments (list, optional): 첨부 파일 경로 리스트
        addon_subject (str, optional): 추가 제목
    """
    if not all([AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY]):
        logger.error("AWS credentials not found in environment variables")
        raise ValueError("AWS credentials not properly configured")

    ses_client = boto3.client(
        "ses",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION,
    )

    # 수신자를 리스트로 변환
    if isinstance(recipient, str):
        recipient = [recipient]

    # CC와 BCC 주소가 None이면 빈 리스트로 초기화
    cc_addresses = cc_addresses or []
    bcc_addresses = bcc_addresses or []

    try:
        # HTML 본문 생성
        addon_subject_str = "" if not addon_subject else f"{addon_subject}"
        body_html = f"""
            <html>
                <body>
                    <h2>{subject}</h2>
                    {addon_subject_str}
                    <div>{body}</div>
                </body>
            </html>
        """

        # HTML 본문 파트 생성
        part_html = MIMEText(body_html, 'html')

        # 첨부 파일 파트 리스트 생성
        attachment_parts = []
        if attachments:
            for file_path in attachments:
                if not os.path.exists(file_path):
                    logger.warning(f"Attachment not found: {file_path}")
                    continue

                filename = os.path.basename(file_path)
                mime_type, _ = mimetypes.guess_type(file_path)
                if mime_type is None:
                    mime_type = 'application/octet-stream'

                with open(file_path, 'rb') as file:
                    part = MIMEApplication(file.read())
                    part.add_header('Content-Disposition', 'attachment', filename=filename)
                    attachment_parts.append(part)

        # To/CC 수신자용 메시지와 BCC 수신자용 메시지를 동일한 구조로 생성
        def create_mime_message(to_addrs, cc_addrs=None):
            msg = MIMEMultipart('mixed')
            msg['Subject'] = subject
            msg['From'] = sender
            msg['To'] = ', '.join(to_addrs)
            if cc_addrs:
                msg['CC'] = ', '.join(cc_addrs)
            msg['Date'] = email.utils.formatdate(localtime=True)
            msg['Message-ID'] = email.utils.make_msgid(domain=sender.split('@')[1])

            # HTML 본문 추가
            msg.attach(part_html)

            # 첨부 파일 추가
            for part in attachment_parts:
                msg.attach(part)

            return msg

        # 메일 전송 함수
        def send_ses_email(msg, destinations):
            response = ses_client.send_raw_email(
                Source=sender,
                Destinations=destinations,
                RawMessage={'Data': msg.as_string()}
            )
            return response['MessageId']

        # To와 CC 수신자에게 메일 전송
        if recipient or cc_addresses:
            main_msg = create_mime_message(recipient, cc_addresses)
            msg_id = send_ses_email(main_msg, recipient + cc_addresses)
            logger.info(f"Main email sent! Message ID: {msg_id}")

        # BCC 수신자에게 메일 전송. spam함 안가게 주소를 넣어 준다.
        if bcc_addresses:
            for bcc_address in bcc_addresses:
                # BCC 수신자용 메시지 생성
                bcc_msg = create_mime_message([bcc_address])
                # BCC 수신자에게만 전송
                msg_id = send_ses_email(bcc_msg, [bcc_address])
                logger.info(f"BCC email sent to {bcc_address}! Message ID: {msg_id}")

    except (NoCredentialsError, PartialCredentialsError) as e:
        logger.error(f"Credentials error: {e}")
        raise
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        raise
