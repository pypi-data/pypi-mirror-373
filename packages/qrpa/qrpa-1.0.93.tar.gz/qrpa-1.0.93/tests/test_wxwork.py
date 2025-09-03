from qrpa import WxWorkBot

def test_wxwork_text():
    bot = WxWorkBot('ee5a048a-1b9e-41e4-9382-aa0ee447898f')
    bot.send_text('Hi QSir')

if __name__ == '__main__':
    test_wxwork_text()