from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty
import yaml
import csv


def read_config():
    with open('config.yml') as f:
        try:
            return yaml.load(f, Loader=yaml.FullLoader)
        except yaml.YAMLError as exc:
            print(exc)
            return {}


settings = read_config()
api_id = settings['api_id']
api_hash = settings['api_hash']
phone = settings['phone']

client = TelegramClient(phone, api_id, api_hash)

client.connect()
if not client.is_user_authorized():
    client.send_code_request(phone)
    client.sign_in(phone, input('Enter the code: '))


chats = []
last_date = None
chunk_size = 200
groups = []

result = client(GetDialogsRequest(
    offset_date=last_date,
    offset_id=0,
    offset_peer=InputPeerEmpty(),
    limit=chunk_size,
    hash=0
))
chats.extend(result.chats)

for chat in chats:
    try:
        if chat.megagroup == True:
            groups.append(chat)
    except:
        continue

print('Choose a group to scrape members from:')
for i, g in enumerate(groups):
    print(f'{str(i)}- {g.title}')
g_index = input("Enter a Number: ")
target_group = groups[int(g_index)]

print('Fetching Members...')
all_participants = []
all_participants = client.get_participants(target_group, aggressive=True)

print('Saving In file...')
with open("members.csv", "w", encoding='UTF-8') as f:
    writer = csv.writer(f, delimiter=",", lineterminator="\n")
    writer.writerow(['username', 'user id', 'access hash',
                    'name', 'group', 'group id'])
    for user in all_participants:
        username = user.username if user.username else ""
        first_name = user.first_name if user.first_name else ""
        last_name = user.last_name if user.last_name else ""
        name = f'{first_name} {last_name}'.strip()
        writer.writerow([username, user.id, user.access_hash,
                        name, target_group.title, target_group.id])
print('Members scraped successfully.')
