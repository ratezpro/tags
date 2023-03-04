from LineAPI.akad import *
from LineAPI.linepy import *
from datetime import datetime
from newqr import NewQRLogin
from tools import LiveJSON, FixJSON

import json
import os
import subprocess
import pytz
import time
import threading
import traceback

qrCodev2 = NewQRLogin()
NAME_APP = "CHROMEOS\t2.5.6\tCHROMEOS\t1"
settings = LiveJSON('Json/settings.json')
FixJSON(settings,{
    "authToken": "",
    "admin": {},
    "welcome": {},
    "sendData": {"text": {}, "tag": {}, "picture": {}, "textkick": []},
    "proData": {},
    "funUnsend": {},
    "note": {},
    "album": {},
    "share": {}
    })

"LOGIN CLIENT"
client = LINE("LINETOKEN",appName=NAME_APP)
owner = [client.profile.mid]
oepoll = OEPoll(client)
def mentionAllGroup(to, mids, result):
    parsed_len = len(mids)//20+1
    mention = '@zeroxyuuki\n'
    no = 0
    for point in range(parsed_len):
        mentionees = []
        for mid in mids[point*20:(point+1)*20]:
            no += 1
            result += '%i. %s' % (no, mention)
            slen = len(result) - 12
            elen = len(result) + 3
            mentionees.append({'S': str(slen), 'E': str(elen - 4), 'M': mid})
        if result:
            if result.endswith('\n'): result = result[:-1]
            client.sendMessage(to, result, {'MENTION': json.dumps({'MENTIONEES': mentionees})}, 0)
        result = ''
def runningProMessage():
    global settings
    tz = pytz.timezone("Asia/Bangkok")
    timeNow = datetime.now(tz=tz)
    nowT = datetime.strftime(timeNow,"%H")
    nowM = datetime.strftime(timeNow,"%M")
    nowS = datetime.strftime(timeNow,"%S")
    for group in client.getGroupIdsJoined():
        if group in settings["proData"]:
            if settings["proData"][group]["fun"] == True:
                if settings["proData"][group]["data"] != {}:
                    for i in settings["proData"][group]["data"]:
                        if f"{nowT}/{nowM}/{nowS}" == settings["proData"][group]["data"][i]:
                            time.sleep(1)
                            client.sendMessage(group, i)
def helpMessage():
    help = """คำสั่งทั้งหมด:

- แทค
- จับอ่าน (on/off)
- จับยก (on/off)

คำสั่งเฉพาะแอดมินหรือเจ้าของ:

- settext:list
- settextadd: (ข้อความตั้งรับ);(ข้อความ)
- settextremove: (ข้อความ)
- settextkick:list
- settextkickadd: (ข้อความ)
- settextkickremove: (ข้อความ)
- settexttime:list
- settexttimeadd: (ข้อความ);(ชั่วโมง/นาที/วินาที)
- settexttimeremove: (ข้อความ)
- texttime: (on/off)
- settag:list
- settagadd: (ข้อความ)
- settagremove: (ข้อความ)
- setpicture:list
- setpictureadd: (ข้อความ)
- setpictureremove: (ข้อความ)
- admin:list
- admin:add (@)
- admin:remove (@)
- welcome:(on/off)
- note:(on/off)
- album:(on/off)
- share:(on/off)

- เฉพาะเจ้าของ
- ex (ข้อมูล)"""
    return help
lastText = ""
datalist = []
dataRead = {}
dataTextUnsend = {}
def executeCmd(op):
    global datalist
    global dataRead
    global owner
    global settings
    global lastText
    global dataTextUnsend
    global helpMessage
    global mentionAllGroup
    try:
        if op.type == 13:
            if client.profile.mid in op.param3:
                client.acceptGroupInvitation(op.param1)
        if op.type == 17:
            if op.param1 in settings["welcome"]:
                if settings["welcome"][op.param1]["fun"] == True:
                    client.sendMessage(op.param1, settings["welcome"][op.param1]["Message"])
        if op.type in [25, 26]:
            msg = op.message
            if msg.toType == 2:
                if msg.to not in settings["admin"]:
                    settings["admin"][msg.to] = []
                if msg.to in settings["note"]:
                    if settings["note"][msg.to]["fun"] == True:
                        if msg.contentType == 16 and msg.contentMetadata["serviceType"] == "GB":
                            if msg._from in settings["admin"]:
                                return
                            if msg._from in owner:
                                return
                            try:
                                client.kickoutFromGroup(msg.to, [msg._from])
                            except:
                                pass
                if msg.to in settings["album"]:
                    if settings["album"][msg.to]["fun"] == True:
                        if "LOC_KEY" in msg.contentMetadata and msg.contentMetadata["LOC_KEY"] == "BD":
                            if msg._from in settings["admin"]:
                                return
                            if msg._from in owner:
                                return
                            try:
                                client.kickoutFromGroup(msg.to, [msg._from])
                            except:
                                pass
                if msg.to in settings["share"]:
                    if settings["share"][msg.to]["fun"] == True:
                        if "https://" in msg.text or "http://" in msg.text or "line://" in msg.text or ".com" in msg.text or ".vip" in msg.text or ".net" in msg.text:
                            if msg._from in settings["admin"]:
                                return
                            if msg._from in owner:
                                return
                            try:
                                client.kickoutFromGroup(msg.to, [msg._from])
                            except:
                                pass
                if msg.text in settings["sendData"]["textkick"]:
                    if msg._from not in settings["admin"] or msg._from not in owner:
                        if msg._from in settings["admin"]:
                            return
                        if msg._from in owner:
                            return
                        try:
                            client.kickoutFromGroup(msg.to, [msg._from])
                        except:
                            pass
            if msg.contentType == 0:
                if msg.text is None:
                    return
                if msg.to in settings["sendData"]["text"]:
                    if msg.text in settings["sendData"]["text"][msg.to]:
                        client.sendMessage(msg.to, str(settings["sendData"]["text"][msg.to][msg.text]))
                if msg.to in settings["sendData"]["tag"]:
                    if msg.text in settings["sendData"]["tag"][msg.to]:
                        client.sendMessage(msg.to, client.getContact(settings["sendData"]["tag"][msg.to][msg.text]).displayName)
                        client.sendContact(msg.to, settings["sendData"]["tag"][msg.to][msg.text])
                if msg.to in settings["sendData"]["picture"]:
                    if msg.text in settings["sendData"]["picture"][msg.to]["path"]:
                        client.sendImage(msg.to, settings["sendData"]["picture"][msg.to]["path"][msg.text])
        if op.type in [25, 26]:
            msg = op.message
            if msg.contentType == 0:
                if msg.text is None:
                    return
                if msg.text.lower() == "คำสั่ง":
                    client.sendMessage(msg.to, str(helpMessage()))
                if msg.text.lower() == "แทค":
                    members = [mem.mid for mem in client.getGroup(msg.to).members]
                    mentionAllGroup(msg.to, members, "แทคสามาชิกทั้งหมด:\n")
                if msg.text.lower().startswith("จับอ่าน "):
                    data = msg.text.split("จับอ่าน ")[1]
                    if msg.to not in dataRead:
                        dataRead[msg.to] = {"fun": False, "member": []}
                    if data == "on":
                        if dataRead[msg.to]["fun"] == True:
                            client.sendMessage(msg.to, "เปิดจับอ่านอยู่แล้ว")
                        else:
                            dataRead[msg.to]["fun"] = True
                            client.sendMessage(msg.to, "เปิดจับคนอ่านเสร็จสิ้น")
                    if data == "off":
                        if dataRead[msg.to]["fun"] == False:
                            client.sendMessage(msg.to, "เปิดจับอ่านอยู่แล้ว")
                        else:
                            mentionAllGroup(msg.to, dataRead[msg.to]["member"], "คนอ่านทั้งหมด:\n")
                            del dataRead[msg.to]
                if msg.text.lower().startswith("จับยก "):
                    data = msg.text.split("จับยก ")[1]
                    if msg.to not in settings["funUnsend"]:
                        settings["funUnsend"][msg.to] = False
                    if data == "on":
                        if settings["funUnsend"][msg.to] == True:
                            client.sendMessage(msg.to, "เปิดอยู่แล้ว")
                        else:
                            settings["funUnsend"][msg.to] = True
                            client.sendMessage(msg.to, "เปิดเสร็จสิ้น")
                    if data == "off":
                        if settings["funUnsend"][msg.to] == False:
                            client.sendMessage(msg.to, "ปิดอยู่แล้ว")
                        else:
                            settings["funUnsend"][msg.to] = False
                            client.sendMessage(msg.to, "ปิดเสร็จสิ้น")
                if msg._from in owner:
                    if msg.text.lower().startswith("ex "):
                        text = msg.text.split("ex ")[1]
                        datalist.append(text)
                        try:
                            data = ""
                            n = 1
                            for i in datalist:
                                if n == len(datalist):
                                    data += i
                                else:
                                    data += i + " && "
                                n += 1
                            os.system("cd && " + data)
                            if "cd" not in text:
                                if "/bin/sh: 1:" in subprocess.getoutput("cd && "+data):
                                    datalist.remove(text)
                                client.sendMessage(msg.to, str(subprocess.getoutput("cd && "+data)))
                            else:
                                client.sendMessage(msg.to, data)
                            if text == "cd":
                                datalist = []
                            if "cd " not in text:
                                datalist.remove(text)
                        except Exception as e:
                            client.sendMessage(msg.to, str(e))
                            datalist.remove(text)
                if msg._from in owner:
                    if msg.text.lower() == "settext:list":
                        if msg.to not in settings["sendData"]["text"]:
                            settings["sendData"]["text"][msg.to] = {}
                        if settings["sendData"]["text"][msg.to] == {}:
                            client.sendMessage(msg.to, "ไม่พบข้อมูลในกลุ่มนี้")
                        else:
                            n = 1
                            text = "ข้อความที่ตั้งทั้งหมด:"
                            for i in settings["sendData"]["text"][msg.to]:
                                text += f'\n{n}. {i};;{settings["sendData"]["text"][msg.to][i]}'
                                n += 1
                            client.sendMessage(msg.to, text)
                    if msg.text.lower().startswith("settextadd: "):
                        datatext = msg.text.split(":")
                        if msg.to not in settings["sendData"]["text"]:
                            settings["sendData"]["text"][msg.to] = {}
                        if datatext[1] not in settings["sendData"]["text"][msg.to]:
                            if ";" in datatext[1]:
                                tdata = datatext[1].split(";")
                                settings["sendData"]["text"][msg.to][tdata[0]] = tdata[1]
                                client.sendMessage(msg.to, "ตั้งค่าเสร็จสิ้น")
                            else:
                                client.sendMessage(msg.to, "ตั่งค่าไม่เสร็จสิ้น")
                        else:
                            client.sendMessage(msg.to, "ตั้งไว้อยู่แล้ว")
                    if msg.text.lower().startswith("settextremove: "):
                        datatext = msg.text.split(":")
                        if msg.to not in settings["sendData"]["text"]:
                            settings["sendData"]["text"][msg.to] = {}
                        if datatext[1] in settings["sendData"]["text"][msg.to]:
                            del settings["sendData"]["text"][msg.to][datatext[1]]
                            client.sendMessage(msg.to, "ลบค่าเสร็จสิ้น")
                        else:
                            client.sendMessage(msg.to, "ไม่ได้ตั้งไว้อยู่แล้ว")
                    if msg.text.lower() == "settextkick:list":
                        if settings["sendData"]["textkick"] == []:
                            client.sendMessage(msg.to, "ไม่พบข้อมูล")
                        else:
                            n = 1
                            text = "ข้อความที่ตั้งทั้งหมด:"
                            for i in settings["sendData"]["textkick"]:
                                text += f'\n{n}. {i}'
                                n += 1
                            client.sendMessage(msg.to, text)
                    if msg.text.lower().startswith("settextkickadd: "):
                        datatext = msg.text.split(":")
                        if datatext[1] not in settings["sendData"]["textkick"]:
                            settings["sendData"]["textkick"].append(datatext[1])
                            client.sendMessage(msg.to, "ตั้งค่าเสร็จสิ้น")
                        else:
                            client.sendMessage(msg.to, "ตั้งไว้อยู่แล้ว")
                    if msg.text.lower().startswith("settextkickremove: "):
                        datatext = msg.text.split(":")
                        if datatext[1] in settings["sendData"]["textkick"]:
                            settings["sendData"]["textkick"].remove(datatext[1])
                            client.sendMessage(msg.to, "ลบค่าเสร็จสิ้น")
                        else:
                            client.sendMessage(msg.to, "ไม่ได้ตั้งไว้อยู่แล้ว")
                    if msg.text.lower() == "settexttime:list":
                        if msg.to not in settings["proData"]:
                            settings["proData"][msg.to] = {"fun": False, "data": {}}
                        if settings["proData"][msg.to]["data"] == {}:
                            client.sendMessage(msg.to, "ไม่พบข้อมูลในกลุ่มนี้")
                        else:
                            n = 1
                            text = "ข้อความที่ตั้งทั้งหมด:"
                            for i in settings["proData"][msg.to]["data"]:
                                text += f'\n{n}. {i};;{settings["proData"][msg.to]["data"][i]}'
                                n += 1
                            client.sendMessage(msg.to, text)
                    if msg.text.lower().startswith("settexttimeadd: "):
                        datatext = msg.text.split(":")
                        if msg.to not in settings["proData"]:
                            settings["proData"][msg.to] = {"fun": False, "data": {}}
                        if datatext[1] not in settings["proData"][msg.to]["data"]:
                            if ";" in datatext[1]:
                                tdata = datatext[1].split(";")
                                settings["proData"][msg.to]["data"][tdata[0]] = tdata[1]
                                client.sendMessage(msg.to, "ตั้งค่าเสร็จสิ้น")
                            else:
                                client.sendMessage(msg.to, "ตั่งค่าไม่เสร็จสิ้น")
                        else:
                            client.sendMessage(msg.to, "ตั้งไว้อยู่แล้ว")
                    if msg.text.lower().startswith("settexttimeremove: "):
                        datatext = msg.text.split(":")
                        if msg.to not in settings["proData"]:
                            settings["proData"][msg.to] = {"fun": False, "data": {}}
                        if datatext[1] in settings["proData"][msg.to]["data"]:
                            del settings["proData"][msg.to]["data"][datatext[1]]
                            client.sendMessage(msg.to, "ลบค่าเสร็จสิ้น")
                        else:
                            client.sendMessage(msg.to, "ไม่ได้ตั้งไว้อยู่แล้ว")
                    if msg.text.lower().startswith("texttime: "):
                        datatext = msg.text.split("texttime: ")
                        if msg.to not in settings["proData"]:
                            settings["proData"][msg.to] = {"fun": False, "data": {}}
                        if datatext[1] == "on":
                            if settings["proData"][msg.to]["fun"] == True:
                                client.sendMessage(msg.to, "เปิดอยู่แล้ว")
                            else:
                                settings["proData"][msg.to]["fun"] = True
                                client.sendMessage(msg.to, "เปิดเสร็จสิ้น")
                        if datatext[1] == "off":
                            if settings["proData"][msg.to]["fun"] == False:
                                client.sendMessage(msg.to, "ปิดอยู่แล้ว")
                            else:
                                settings["proData"][msg.to]["fun"] = False
                                client.sendMessage(msg.to, "ปิดเสร็จสิ้น")
                    if msg.text.lower() == "settag:list":
                        if msg.to not in settings["sendData"]["tag"]:
                            settings["sendData"]["tag"][msg.to] = {}
                        if settings["sendData"]["tag"][msg.to] == {}:
                            client.sendMessage(msg.to, "ไม่พบข้อมูลในกลุ่มนี้")
                        else:
                            n = 1
                            text = "ข้อความที่ตั้งทั้งหมด:"
                            for i in settings["sendData"]["tag"][msg.to]:
                                text += f'\n{n}. {i};;{client.getContact(settings["sendData"]["tag"][i]).displayName}'
                                n += 1
                            client.sendMessage(msg.to, text)
                    if msg.text.lower().startswith("settagadd: "):
                        datatext = msg.text.split(":")
                        if "MENTION" in msg.contentMetadata:
                            if msg.to not in settings["sendData"]["tag"]:
                                settings["sendData"]["tag"][msg.to] = {}
                            targets = [i["M"] for i in eval(msg.contentMetadata["MENTION"])["MENTIONEES"]]
                            if len(targets) > 1:
                                client.sendMessage(msg.to, "ตั้งแท็กได้คนเดียวเท่านั้น!")
                            else:
                                if datatext[1] not in settings["sendData"]["tag"][msg.to]:
                                    settings["sendData"]["tag"][msg.to][datatext[1]] = targets[0]
                                    client.sendMessage(msg.to, "ตั้งค่าเสร็จสิ้น")
                                else:
                                    client.sendMessage(msg.to, "ตั้งไว้อยู่แล้ว")
                    if msg.text.lower().startswith("settagremove: "):
                        datatext = msg.text.split(":")
                        if "MENTION" in msg.contentMetadata:
                            if msg.to not in settings["sendData"]["tag"]:
                                settings["sendData"]["tag"][msg.to] = {}
                            targets = [i["M"] for i in eval(msg.contentMetadata["MENTION"])["MENTIONEES"]]
                            if len(targets) > 1:
                                client.sendMessage(msg.to, "ลบแท็กได้คนเดียวเท่านั้น!")
                            else:
                                if datatext[1] in settings["sendData"]["tag"][msg.to]:
                                    del settings["sendData"]["tag"][msg.to][datatext[1]]
                                    client.sendMessage(msg.to, "ลบค่าเสร็จสิ้น")
                                else:
                                    client.sendMessage(msg.to, "ไม่ได้ตั้งไว้อยู่แล้ว")
                    if msg.text.lower() == "setpicture:list":
                        if msg.to not in settings["sendData"]["picture"]:
                            settings["sendData"]["picture"][msg.to] = {"path": {}, "fun": False}
                        if settings["sendData"]["picture"][msg.to]["path"] == {}:
                            client.sendMessage(msg.to, "ไม่พบข้อมูลในกลุ่มนี้")
                        else:
                            n = 1
                            text = "ข้อความที่ตั้งทั้งหมด:"
                            for i in settings["sendData"]["picture"][msg.to]["path"]:
                                text += f'\n{n}. {i}'
                                n += 1
                            client.sendMessage(msg.to, text)
                    if msg.text.lower().startswith("setpictureadd: "):
                        datatext = msg.text.split(":")
                        if msg.to not in settings["sendData"]["picture"]:
                            settings["sendData"]["picture"][msg.to] = {"path": {}, "fun": False}
                        if datatext[1] not in settings["sendData"]["picture"][msg.to]["path"]:
                            lastText = datatext[1]
                            settings["sendData"]["picture"][msg.to]["fun"] = True
                            client.sendMessage(msg.to, "ส่งรูปมา")
                        else:
                            client.sendMessage(msg.to, "ตั้งไว้อยู่แล้ว")
                    if msg.text.lower().startswith("setpictureremove: "):
                        datatext = msg.text.split(":")
                        if msg.to not in settings["sendData"]["picture"]:
                            settings["sendData"]["picture"][msg.to] = {"path": {}, "fun": False}
                        if datatext[1] in settings["sendData"]["picture"][msg.to]["path"]:
                            lastText = datatext[1]
                            settings["sendData"]["picture"][msg.to]["fun"] = False
                            del settings["sendData"]["picture"][msg.to]["path"][datatext[1]]
                            client.sendMessage(msg.to, "ลบเสร็จสิ้น")
                        else:
                            client.sendMessage(msg.to, "ไม่ได้ตั้งไว้อยู่แล้ว")
                    if msg.text.lower() == "admin:list":
                       if settings["admin"][msg.to] == []:
                           client.sendMessage(msg.to, "ไม่พบ")
                       else:
                           mentionAllGroup(msg.to, members, "แอดมินกลุ่มนี้ทั้งหมด:\n")
                    if msg.text.lower().startswith("admin:add "):
                        if "MENTION" in msg.contentMetadata:
                            targets = [i["M"] for i in eval(msg.contentMetadata["MENTION"])["MENTIONEES"]]
                            for target in targets:
                                if target in settings["admin"]:
                                    client.sendMessage(msg.to, "อยู่ในแอดมินแล้ว")
                                else:
                                    settings["admin"][msg.to].append(target)
                                    client.sendMessage(msg.to, "เพิ่มเสร็จสิ้น")
                    if msg.text.lower().startswith("admin:remove "):
                        if "MENTION" in msg.contentMetadata:
                            targets = [i["M"] for i in eval(msg.contentMetadata["MENTION"])["MENTIONEES"]]
                            for target in targets:
                                if target not in settings["admin"]:
                                    client.sendMessage(msg.to, "ไม่ได้อยู่ในแอดมินแล้ว")
                                else:
                                    settings["admin"][msg.to].remove(target)
                                    client.sendMessage(msg.to, "ลบเสร็จสิ้น")
                    if msg.text.lower().startswith("welcome:"):
                        datatext = msg.text.split("welcome:")
                        if msg.to not in settings["welcome"]:
                            settings["welcome"][msg.to] = {"fun": False, "Message": "ยินดีต้อนรับเข้าห้องครับ"}
                        if datatext[1] == "on":
                            if settings["welcome"][msg.to]["fun"] == True:
                                client.sendMessage(msg.to, "เปิดอยู่แล้ว")
                            else:
                                settings["welcome"][msg.to]["fun"] = True
                                client.sendMessage(msg.to, "เปิดเสร็จสิ้น")
                        if datatext[1] == "off":
                            if settings["welcome"][msg.to]["fun"] == False:
                                client.sendMessage(msg.to, "ปิดอยู่แล้ว")
                            else:
                                settings["welcome"][msg.to]["fun"] = False
                                client.sendMessage(msg.to, "ปิดเสร็จสิ้น")
                    if msg.text.lower().startswith("welcome:message "):
                        datatext = msg.text.split("welcome:message ")
                        if msg.to not in settings["welcomeGroup"]:
                            settings["welcomeGroup"][msg.to] = {"fun": False, "Message": "ยินดีต้อนรับเข้าห้องครับ"}
                        if settings["welcomeGroup"][msg.to]["Message"] == datatext[1]:
                            client.sendMessage(msg.to, "คุณตั้งไว้อยู่แล้ว")
                        else:
                            settings["welcomeGroup"][msg.to]["Message"] = datatext[1]
                            client.sendMessage(msg.to, "ตั้งเสร็จสิ้น")
                    if msg.text.lower().startswith("note:"):
                        datatext = msg.text.split("note:")
                        if msg.to not in settings["note"]:
                            settings["note"][msg.to] = {"fun": False}
                        if datatext[1] == "on":
                            if settings["note"][msg.to]["fun"] == True:
                                client.sendMessage(msg.to, "เปิดอยู่แล้ว")
                            else:
                                settings["note"][msg.to]["fun"] = True
                                client.sendMessage(msg.to, "เปิดเสร็จสิ้น")
                        if datatext[1] == "off":
                            if settings["note"][msg.to]["fun"] == False:
                                client.sendMessage(msg.to, "ปิดอยู่แล้ว")
                            else:
                                settings["note"][msg.to]["fun"] = False
                                client.sendMessage(msg.to, "ปิดเสร็จสิ้น")
                    if msg.text.lower().startswith("album:"):
                        datatext = msg.text.split("album:")
                        if msg.to not in settings["album"]:
                            settings["album"][msg.to] = {"fun": False}
                        if datatext[1] == "on":
                            if settings["album"][msg.to]["fun"] == True:
                                client.sendMessage(msg.to, "เปิดอยู่แล้ว")
                            else:
                                settings["album"][msg.to]["fun"] = True
                                client.sendMessage(msg.to, "เปิดเสร็จสิ้น")
                        if datatext[1] == "off":
                            if settings["album"][msg.to]["fun"] == False:
                                client.sendMessage(msg.to, "ปิดอยู่แล้ว")
                            else:
                                settings["album"][msg.to]["fun"] = False
                                client.sendMessage(msg.to, "ปิดเสร็จสิ้น")
                    if msg.text.lower().startswith("share:"):
                        datatext = msg.text.split("share:")
                        if msg.to not in settings["share"]:
                            settings["share"][msg.to] = {"fun": False}
                        if datatext[1] == "on":
                            if settings["share"][msg.to]["fun"] == True:
                                client.sendMessage(msg.to, "เปิดอยู่แล้ว")
                            else:
                                settings["share"][msg.to]["fun"] = True
                                client.sendMessage(msg.to, "เปิดเสร็จสิ้น")
                        if datatext[1] == "off":
                            if settings["share"][msg.to]["fun"] == False:
                                client.sendMessage(msg.to, "ปิดอยู่แล้ว")
                            else:
                                settings["share"][msg.to]["fun"] = False
                                client.sendMessage(msg.to, "ปิดเสร็จสิ้น")
            if msg.contentType == 1:
                if msg._from in settings["admin"][msg.to] or msg._from in owner:
                    if settings["sendData"]["picture"][msg.to]["fun"] == True:
                        try:
                            path = client.downloadObjectMsg(msg.id)
                            settings["sendData"]["picture"][msg.to]["path"][lastText] = path
                            settings["sendData"]["picture"][msg.to]["fun"] = False
                            lastText = ""
                            client.sendMessage(msg.to, "ตั้งค่าเสร็จสิ้น")
                        except:
                            traceback.print_exc()
        if op.type == 26:
            msg = op.message
            if msg.to in settings["funUnsend"]:
                if settings["funUnsend"][msg.to] == True:
                    if msg.contentType == 0:
                        try:
                            path = msg.text
                            if msg.to not in dataTextUnsend:
                                dataTextUnsend[msg.to] = {}
                            dataTextUnsend[msg.to][msg.id] = {"text": path, "from": msg._from}
                        except:
                            traceback.print_exc()
                    if msg.contentType == 1:
                        try:
                            path = client.downloadObjectMsg(msg.id)
                            if msg.to not in dataTextUnsend:
                                dataTextUnsend[msg.to] = {}
                            dataTextUnsend[msg.to][msg.id] = {"image": path, "from": msg._from}
                        except:
                            traceback.print_exc()
                    if msg.contentType == 2:
                        try:
                            path = client.downloadObjectMsg(msg.id)
                            if msg.to not in dataTextUnsend:
                                dataTextUnsend[msg.to] = {}
                            dataTextUnsend[msg.to][msg.id] = {"video": path, "from": msg._from}
                        except:
                            traceback.print_exc()
                    if msg.contentType == 3:
                        try:
                            path = client.downloadObjectMsg(msg.id)
                            if msg.to not in dataTextUnsend:
                                dataTextUnsend[msg.to] = {}
                            dataTextUnsend[msg.to][msg.id] = {"audio": path, "from": msg._from}
                        except:
                            traceback.print_exc()
                    if msg.contentType == 7:
                        try:
                            path = f'http://dl.stickershop.line.naver.jp/stickershop/v1/sticker/{msg.contentMetadata["STKID"]}/android/sticker.png'
                            if msg.to not in dataTextUnsend:
                                dataTextUnsend[msg.to] = {}
                            dataTextUnsend[msg.to][msg.id] = {"sticker" :path, "from": msg._from}
                        except:
                            traceback.print_exc()
                    if msg.contentType == 13:
                        try:
                            path = msg.contentMetadata["mid"]
                            if msg.to not in dataTextUnsend:
                                dataTextUnsend[msg.to] = {}
                            dataTextUnsend[msg.to][msg.id] = {"contact" :path, "from": msg._from}
                        except:
                            traceback.print_exc()
                    if msg.contentType == 14:
                        try:
                            path = client.downloadObjectMsg(msg.id)
                            if msg.to not in dataTextUnsend:
                                dataTextUnsend[msg.to] = {}
                            dataTextUnsend[msg.to][msg.id] = {"file" :path, "from": msg._from}
                        except:
                            traceback.print_exc()
        if op.type == 55:
            if op.param1 in dataRead:
                if dataRead[op.param1]["fun"] == True:
                    if op.param2 not in dataRead[op.param1]["member"]:
                        dataRead[op.param1]["member"].append(op.param2)
                        client.sendMentionV2(op.param1, f'{len(dataRead[op.param1]["member"])}. @!', [op.param2])
        if op.type == 65:
            if op.param1 in settings["funUnsend"]:
                if settings["funUnsend"][op.param1] == True:
                    if op.param1 in dataTextUnsend:
                        if op.param2 in dataTextUnsend[op.param1]:
                            if "text" in dataTextUnsend[op.param1][op.param2]:
                                client.sendMessage(op.param1, dataTextUnsend[op.param1][op.param2]["text"])
                                client.sendMessage(op.param1, f'ผู้ส่งข้อความคือ: {client.getContact(dataTextUnsend[op.param1][op.param2]["from"]).displayName}')
                                del dataTextUnsend[op.param1][op.param2]
                            if "image" in dataTextUnsend[op.param1][op.param2]:
                                client.sendImage(op.param1, dataTextUnsend[op.param1][op.param2]["image"])
                                client.sendMessage(op.param1, f'ผู้ส่งภาพนี้คือ: {client.getContact(dataTextUnsend[op.param1][op.param2]["from"]).displayName}')
                                del dataTextUnsend[op.param1][op.param2]
                            if "video" in dataTextUnsend[op.param1][op.param2]:
                                client.sendVideo(op.param1, dataTextUnsend[op.param1][op.param2]["video"])
                                client.sendMessage(op.param1, f'ผู้ส่งคริปนี้คือ: {client.getContact(dataTextUnsend[op.param1][op.param2]["from"]).displayName}')
                                del dataTextUnsend[op.param1][op.param2]
                            if "audio" in dataTextUnsend[op.param1][op.param2]:
                                client.sendAudio(op.param1, dataTextUnsend[op.param1][op.param2]["audio"])
                                client.sendMessage(op.param1, f'ผู้ส่งเสียงนี้คือ: {client.getContact(dataTextUnsend[op.param1][op.param2]["from"]).displayName}')
                                del dataTextUnsend[op.param1][op.param2]
                            if "sticker" in dataTextUnsend[op.param1][op.param2]:
                                client.sendImageWithURL(op.param1, dataTextUnsend[op.param1][op.param2]["sticker"])
                                client.sendMessage(op.param1, f'ผู้ส่งสติ๊กเกอร์นี้คือ: {client.getContact(dataTextUnsend[op.param1][op.param2]["from"]).displayName}')
                                del dataTextUnsend[op.param1][op.param2]
                            if "contact" in dataTextUnsend[op.param1][op.param2]:
                                client.sendContact(op.param1, dataTextUnsend[op.param1][op.param2]["contact"])
                                client.sendMessage(op.param1, f'ผู้ส่งคอนแท็กนี้คือ: {client.getContact(dataTextUnsend[op.param1][op.param2]["from"]).displayName}')
                                del dataTextUnsend[op.param1][op.param2]
                            if "file" in dataTextUnsend[op.param1][op.param2]:
                                client.sendFile(op.param1, dataTextUnsend[op.param1][op.param2]["file"])
                                client.sendMessage(op.param1, f'ผู้ส่งไฟล์นี้คือ: {client.getContact(dataTextUnsend[op.param1][op.param2]["from"]).displayName}')
                                del dataTextUnsend[op.param1][op.param2]
    except:
        traceback.print_exc()
if __name__ == "__main__":
    while True:
        ops = oepoll.singleTrace(count=50)
        try:
            if ops is not None:
                for op in ops:
                    if op.type != 0:
                        oepoll.setRevision(op.revision)
                        executeCmd(op)
                        runningProMessage()
        except:
            traceback.print_exc()