from datetime import datetime
from email import encoders
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart

from django.core.mail import EmailMessage
from pgp import armor, read_key
from pgp.message import TextMessage


def send_email(recipient, subject, body, connection=None):
	key = recipient.contact_information.pgp_key
	if key:
		headers, body = encrypt_email(key, body)
	else:
		headers = {}
	EmailMessage(subject, body, to=(recipient.email,), headers=headers, connection=connection).send()


def encrypt_email(key, body):
	key = read_key(key, True)
	message = TextMessage(body, 'email', datetime.now())
	message = message.public_key_encrypt(9, key)  # 9 is AES-256
	message_packets = message.to_packets()
	message_data = b''.join(map(bytes, message_packets))
	armored_message = armor.ASCIIArmor(armor.PGP_MESSAGE, message_data)

	enc = MIMEApplication(
		_data=str(armored_message),
		_subtype='octet-stream; name="encrypted.asc"',
		_encoder=encoders.encode_7or8bit)
	enc['Content-Description'] = 'OpenPGP encrypted message'
	enc['Content-Disposition'] = 'inline; filename="encrypted.asc"'
	enc.set_charset('us-ascii')

	control = MIMEApplication(
		_data='Version: 1\n',
		_subtype='pgp-encrypted',
		_encoder=encoders.encode_7or8bit)
	control.set_charset('us-ascii')
	control['Content-Description'] = 'PGP/MIME version identification'

	encmsg = MIMEMultipart(
		'encrypted',
		protocol='application/pgp-encrypted')
	encmsg.attach(control)
	encmsg.attach(enc)

	# Remove the header.
	body = '\n\n'.join(encmsg.as_string().split('\n\n')[1:])
	headers = {k: v for k, v in encmsg.items()}
	return headers, body
