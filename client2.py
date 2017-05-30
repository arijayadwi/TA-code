import sys
import pjsua as pj
import wave
from time import sleep

LOG_LEVEL=3
current_call = None
# Logging callback
def log_cb(level, str, len):
    print str,
# Callback to receive events from account
class MyAccountCallback(pj.AccountCallback):
    def __init__(self, account=None):
        pj.AccountCallback.__init__(self, account)
    # Notification on incoming call
    def on_incoming_call(self, call):
        global current_call
        if current_call:
            call.answer(486, "Busy")
            return

        print "Incoming call from ", call.info().remote_uri
        print "Press 'a' to answer"
        current_call = call
        call_cb = MyCallCallback(current_call)
        current_call.set_callback(call_cb)
        current_call.answer(180)

# Callback to receive events from Call
class MyCallCallback(pj.CallCallback):
    def __init__(self, call=None):
        pj.CallCallback.__init__(self, call)
    # Notification when call state has changed
    def on_state(self):
        global current_call
        print "Call with", self.call.info().remote_uri,
        print "is", self.call.info().state_text,
        print "last code =", self.call.info().last_code,
        print "(" + self.call.info().last_reason + ")"

        if self.call.info().state == pj.CallState.DISCONNECTED:
            current_call = None
            print 'Current call is', current_call
        # elif self.call.info().state == pj.CallState.CONFIRMED:
        #     #Call is Answred
        #     print "Call Answred"
        #     wfile = wave.open("virgoun.wav")
        #     time = (1.0 * wfile.getnframes ()) / wfile.getframerate ()
        #     print str(time) + "ms"
        #     wfile.close()
        #     call_slot = self.call.info().conf_slot
        #     self.wav_player_id=pj.Lib.instance().create_player('virgoun.wav',loop=False)
        #     self.wav_slot=pj.Lib.instance().player_get_slot(self.wav_player_id)
        #     pj.Lib.instance().conf_connect(self.wav_slot, call_slot)
            #sleep(time)
            #pj.Lib.instance().player_destroy(self.wav_player_id)
            #self.call.hangup()
            #in_call = False
    # Notification when call's media state has changed.
    def on_media_state(self):
        if self.call.info().media_state == pj.MediaState.ACTIVE:
            # Connect the call to sound device
            call_slot = self.call.info().conf_slot
            # self.wav_player_id=pj.Lib.instance().create_player('virgoun.wav',loop=False)
            # self.wav_slot=pj.Lib.instance().player_get_slot(self.wav_player_id)
            # print "id wav " + str(self.wav_player_id)
            # print "id wav slot " + str(self.wav_slot)
            pj.Lib.instance().conf_connect(call_slot, 0)
            pj.Lib.instance().conf_connect(0, call_slot)
            # self.wav_player_id=pj.Lib.instance().create_player('09_ONE_OK_ROCK_Wherever_You_Are.wav',loop=False)
            # pj.Lib.instance().conf_connect(call_slot, self.wav_slot)
            # pj.Lib.instance().conf_connect(self.wav_slot, call_slot)
            # pj.Lib.instance().conf_connect(call_slot, self.wav_slot)
            print "Media is now active"
        else:
            print "Media is inactive"
# Function to make call
def make_call(uri):
    try:
        print "Making call to", uri
        return acc.make_call(uri, cb=MyCallCallback())
    except pj.Error, e:
        print "Exception: " + str(e)
        return None

# Create library instance
lib = pj.Lib()
try:
    # Init library with default config and some customized
    # logging config.
    lib.init(log_cfg = pj.LogConfig(level=LOG_LEVEL, callback=log_cb))
    # lib.set_null_snd_dev()
    # Create UDP transport which listens to any available port
    transport = lib.create_transport(pj.TransportType.UDP,
                                     pj.TransportConfig(0))
    print "\nListening on", transport.info().host,
    print "port", transport.info().port, "\n"

    # Start the library
    lib.start()

    # Create local account
    # server=raw_input("Enter IP address of the Server: ")
    server = "10.151.34.221"
    user=raw_input("Enter Username: ")
    # ab1=raw_input("Enter Password: ")
    ab1 = "123456"
    ab3 = "y"
    # ab2=raw_input("Do you want to use the display name same as the username  Y/N ??")
    # if ab2=="y" or ab2=="Y":
    #     ab3=user
    # else:
    #     ab3=raw_input("Enter Display Name: ")

    acc_conf = pj.AccountConfig(domain = server, username = user, password =ab1, display = ab3)

                              # registrar = 'sip:'+ab4+':5060', proxy = 'sip:'+ab4+':5060')

    acc_conf.id ="sip:"+user
    acc_conf.reg_uri ='sip:'+server+':'+str(transport.info().port)
    acc_conf.use_srtp = 2
    acc_conf.srtp_secure_signaling = 0
    acc_callback = MyAccountCallback(acc_conf)
    acc = lib.create_account(acc_conf,cb=acc_callback)

    # creating instance of AccountCallback class

    acc.set_callback(acc_callback)

    print('\n')
    print "Registration Complete-----------"
    print('Status= ',acc.info().reg_status, \
         '(' + acc.info().reg_reason + ')')

    #acc = lib.create_account_for_transport(transport, cb=MyAccountCallback())
    # If argument is specified then make call to the URI
    if len(sys.argv) > 1:
        lck = lib.auto_lock()
        current_call = make_call(sys.argv[1])
        print 'Current call is', current_call
        del lck
    my_sip_uri = acc_conf.id + "@" + transport.info().host + \
                 ":" + str(transport.info().port)
    # Menu loop
    while True:
        print "My SIP URI is", my_sip_uri
        print "Menu:  m=make call, h=hangup call, a=answer call, q=quit"
        input = sys.stdin.readline().rstrip("\r\n")
        if input == "m":
            if current_call:
                print "Already have another call"
                continue
            print "Enter destination URI to call: ",
            input = sys.stdin.readline().rstrip("\r\n")
            if input == "":
                continue
            lck = lib.auto_lock()
            current_call = make_call(input)
            del lck
        elif input == "h":
            if not current_call:
                print "There is no call"
                continue
            current_call.hangup()
        elif input == "a":
            if not current_call:
                print "There is no call"
                continue
            current_call.answer(200)
        elif input == "q":
            break
    # Shutdown the library
    transport = None
    acc.delete()
    acc = None
    lib.destroy()
    lib = None
except pj.Error, e:
    print "Exception: " + str(e)
    lib.destroy()
    lib = None
