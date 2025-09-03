# p = Popen(["node", dirname(__file__) + "/req.mjs"], stdout=PIPE)
# out = p.stdout.read().decode()

# s = Session()
# s.headers = {"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"}
# get_login = s.get("https://account.volet.com/login")
#
# hdrs = {
#     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
#     "Content-Type": "application/x-www-form-urlencoded",
# }
# data = "j_idt36=j_idt36&j_username=mixartemev%40gmail.com&j_password=mixfixX98&loginToAdvcashButton=Log+in&" \
#        "screenSize=2048x1280&browserLanguage=ru&cookiesEnables=true&platform=MacIntel&colorDepth=24&timeZone=180&" \
#        "plugins=PDF+Viewer%7CChrome+PDF+Viewer%7CChromium+PDF+Viewer%7CMicrosoft+Edge+PDF+Viewer%7CWebKit+built-in+PDF"\
#        "&javax.faces.ViewState="+dct.pop('jfvs')
# login = s.post("https://account.volet.com/login", data, headers=hdrs, cookies=dct)
# sleep(0.6)

# data = f"j_idt30=j_idt30&otpId={code}&screenWidth=2048&screenHeight=1280"
# javax.faces.ViewState=5949640769466059488%3A-1631264174981316196&javax.faces.source=checkOtpButton
# &javax.faces.partial.event=click&javax.faces.partial.execute=checkOtpButton%20%40component
# &javax.faces.partial.render=%40component&org.richfaces.ajax.component=checkOtpButton
# &checkOtpButton=checkOtpButton&AJAX%3AEVENTS_COUNT=1&javax.faces.partial.ajax=true
# otp_resp = s.post("https://account.volet.com/login/otp", data=data)
