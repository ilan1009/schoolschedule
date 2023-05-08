# School Schedule
Discord bot that retrieves changes from my high-schools custom website using selenium, and displays them via discord embeds.

### Installation
```
git clone github.com/ilan1009/schoolschedule
cd schoolschedule  # Navigate to folder
pip install -r requirements.txt
```
Create a bot in discords developer portal and get the token. Put it in vars/token.txt
```
python3 main.py
```
### Usage
My recommendation is that you have one channel where only admins can send messages, where you will send the schedule (via $send), and users will use that. The embed will stay updated and users can select their classes and specific days of the week. This will also save resources on your host device.

Other than that, users can use $send {day, optional} and access the schedule view.

## EXAMPLE:
![Image of the new embed's style](https://i.imgur.com/2KVEoLL.png)
