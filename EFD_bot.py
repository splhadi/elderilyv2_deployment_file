
import gtts
from telebot import types
import GCP_class
import ast
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import random
from apscheduler.schedulers.background import BackgroundScheduler
from plotly.subplots import make_subplots


bucket_name = "ee4002d_bucket"
# authentication details
jsonfile="cred_details.json"
server = GCP_class.Server(bucket_name, jsonfile)
#key = "S129793.02-123"

import telebot

TOKEN = "5649276466:AAEA6339HRIFo55uUizfct69_NnRX7uxIc4"
bot = telebot.TeleBot(TOKEN)


def verify_chatid():
	unit = server.retrieve_file_string("unit_location.txt")
	data = unit.split("\r\n")
	unit_data = [i.split(",") for i in data if len(i) > 1]
	postal=[i[3] for i in unit_data]
	chatid=[]
	for item in postal:
		direc_item = "details"
		detail_direc = server.get_directory(item, direc_item)
		data = server.retrieve_file_string(detail_direc)
		res = ast.literal_eval(data)
		chatid.append(str(res['bio']['caretaker']['chat_ID']))
	#print(chatid)
	return [postal,chatid,[4 for i in postal]]
	#return [["S129793.02-123"], ["463491073"],[4]]


list_chatid = verify_chatid()


print("chatid list:",list_chatid)
def fall_priority(f2d,f3d,fps):

	#simulation variables for testing
	#f2d = 'dfall'
	#f3d = 'lying'
	#fps = "True"

	count=4
	item=[]
	if f2d=="fall":
		count-=1
		item.append("2D Lidar")
	if fps=="True":
		count-=1
		item.append("Pressure Sensor")

	if f3d=="unconscious" and (f2d=="fall"):
		count-=1
		item.append("3D Lidar")

	return count,item
#APscheduler to detect fall

unit_priority={}
def fall_check():
	print("Beginning fall check...")
	#this will be the main fall check for all the detected falls
	timer=10 #in minutes, set this according to how long interval between fall alarms should be

	#simulated a local list_chatid first before connecting outside
	#list_chatid=[["S129793.02-123"], ["463491073"],[4]]

	#chat id used for reference
	for index, key in enumerate(list_chatid[0]):

		try:
			directory = server.get_directory(key, "2d_result")
			fall_2d = server.retrieve_file_string(directory)
		except:
			print("Download error encounted in fall_check() in EFD_bot.py for fall_2d")
			fall_2d = "Error"

		try:
			directory = server.get_directory(key, "3d_result")
			fall_3d = server.retrieve_file_string(directory)
		except:
			print("Download error encounted in fall_check() in EFD_bot.py for fall_3d")
			fall_3d = "Error"
		try:
			directory = server.get_directory(key, "unconscious_result")
			fall_uncon = server.retrieve_file_string(directory)
		except:
			print("Download error encounted in fall_check() in EFD_bot.py for fall_uncon")
			fall_uncon = "Error"
		try:

			directory = server.get_directory(key, "pressure_result")
			fall_ps = server.retrieve_file_string(directory)
		except:
			print("Download error encounted in fall_check() in EFD_bot.py for fall_ps")
			fall_ps = "Error"


		#directory for acknowledge
		try:
			directory = server.get_directory(key, "acknowledge")
			ack = server.retrieve_file_string(directory)
			ack = ack.split(',')
		except:
			print("Download error encounted in fall_check() in EFD_bot.py for acknowledge.txt")
			now = datetime.now()
			dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
			ack=['Error',dt_string]
		print(ack)

		#get delta time
		time_then=ack[1]#.replace("/","").replace(":","")
		date_time_obj = datetime.strptime(time_then, '%d/%m/%Y %H:%M:%S')
		now = datetime.now()
		delta_time=now-date_time_obj
		min=delta_time.total_seconds()/60



		#print("Status:",fall_2d,fall_3d,fall_ps)
		print("\nChecking: ",key)
		print("Current delta time:", round(min,3),' minutes')
		pri_check,detected_fall_sensors=fall_priority(fall_2d,fall_uncon,fall_ps)
		alert=False

		#send true cmd to mic



		if pri_check==1:   #priority 1
			message="URGENT! Priority 1 detected! All sensors have detected a fall. Please attend immediately!\n\n"
			address="Postal code: "+key+"\n\n"
			misc="Type /acknowledge to confirm. Alternatively type /check_fall to check the Fall detection state."
			#print(message)
			message=message+address+misc
			alert=True
		elif pri_check==2: #priority 2
			message = "Warning! Priority 2 detected! Two sensors have detected a fall. Please attend immediately!\n"
			sensors="Sensors detected: "+",".join(detected_fall_sensors)+"\n"
			address="Postal code: "+key+"\n"
			misc="Type /acknowledge to confirm. Alternatively type /check_fall to check the Fall detection state."
			message = message + sensors + address + misc
			#print(message,sensors)
			alert=True
			pass
		elif pri_check==3: #priority 3
			message = "Caution! Priority 3 detected! One sensor have detected a fall.\n\n"
			sensors="Sensors detected: "+" ".join(detected_fall_sensors)+'\n\n'
			address="Postal code: "+key+"\n\n"
			misc="Type /acknowledge to confirm. Alternatively type /check_fall to check the Fall detection state."
			alert=True
			message = message + sensors + address + misc
			#print(message,sensors)
			pass
		else: #priority 4
			#print("Priority 4: all systems normal")
			message="Priority 4: all systems normal"
			alert=False
			pass

		print("Message issued:",message,"|Alert state:",alert)
		#send cmd to microphone
		send_microphone_cmd(key, alert)

		#alert the user
		if alert:
			#detect alarm first
			print(f"detected alarm, comparing index list_chatid:{list_chatid[2][index]} against pricheck:{pri_check}")
			if (ack[0]=="True" and min>timer) or ack[0]=="False" or list_chatid[2][index]!=pri_check:
				bot.send_message(list_chatid[1][index], message)
				#send alert

			else:
				print("Alert state:",alert,"However no alert need to be send as timer delta=",min,'/',timer)
				#alert less than 10 mins
				pass


		else:

			if ack[0]=="True":
				print("Uploading acknowledgement= false into ",key)
				now = datetime.now()
				dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
				directory = server.get_directory(key, "acknowledge")
				server.upload_string(directory, "False," + dt_string)
				#for alert=False, upload to acknowledge.txt that no acknowledgement has to be done
			else:
				print("Alert set false and no upload done to acknowledge.txt")

		#setting priority no
		list_chatid[2][index] = pri_check

def send_microphone_cmd(key,state):
	direc_item = "mic_cmd"
	now = datetime.now()
	dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
	detail_direc = server.get_directory(key, direc_item)
	server.upload_string(detail_direc, str(state)+ ',' + dt_string)



#add scheduler job
print("Adding scheduling job")
scheduler = BackgroundScheduler()
scheduler.add_job(fall_check, 'interval', seconds=10)

@bot.message_handler(commands=['start'])
def send_welcome(message):
	bot.reply_to(message,"Verifying chat ID...")
	print(message.chat.id,type(message.chat.id))

	if str(message.chat.id) in list_chatid[1]:
		bot.reply_to(message, "Good Evening. This is the Elderly Fall Detection bot. Options are available below:")
		markup = types.ReplyKeyboardMarkup()
		itembtna = types.KeyboardButton('/check_fall')
		itembtnv = types.KeyboardButton('/3DImageLidar')
		item2d = types.KeyboardButton('/2DImageLidar')
		itembtnc = types.KeyboardButton('/microphone')
		itembtnd = types.KeyboardButton('/GetElderlyContact')
		itembtne = types.KeyboardButton('/PressureGraph')
		markup.row(itembtna, itembtnv,item2d)
		markup.row(itembtnc, itembtnd, itembtne)
		bot.send_message(message.chat.id, "Choose an option below:", reply_markup=markup)
	else:
		markup = types.ReplyKeyboardRemove(selective=False)
		bot.send_message(message.chat.id, "Chat ID not verified.\nError 403: Unauthorised access.", reply_markup=markup)
		bot.send_message(message.chat.id, "If you wish to access as caretaker, please access ElderILY Dashboard and sync Chat ID.", reply_markup=markup)


@bot.message_handler(commands=['help'])
def get_list(message):
	item_list='/start	Initialise the bot by displaying the options\n\
/refresh	Developer use to refresh chat ID in the event of data loss\n\
/check_fall	To check all fall detection status\n\
/microphone	To check microphone status and mp3 file\n\
/2DImageLidar	To check 2D image of the lidar\n\
/3DImageLidar	To check 3D scatterplot of lidar\n\
/GetElderlyContact	To retrieve the details of the elderily \n\
/PressureGraph	Create pressure sensor graph from GCP\n\
/cancel or /c	Cancel keyboard selection\n\
/acknowledge	Used when alarm is detected, to prevent spamming of notification\n\
/UpdateChatID	Used to add Chat ID into elderily database\n\
/contact	Developer command for testing contact details\n\
/pauseJob	Developer command to pause fall detection check\n\
/job	Developer command to check status of apschedule on fall detection check\n\
/startJob	Developer command to start fall detection check\n\
 '
	bot.reply_to(message, 'Commands available:\n\n'+item_list)


@bot.message_handler(commands=['refresh'])
def refresh_chatid(message):
	#verify checkid

	bot.reply_to(message, "Clearing list in ChatID...")
	list_chatid.clear()
	l1,l2,l3=verify_chatid()
	list_chatid.append(l1)
	list_chatid.append(l2)
	list_chatid.append(l3)

	bot.reply_to(message, "Chat ID updated!\nlist_chatID: "+str(list_chatid))


	pass
@bot.message_handler(commands=['check_fall'])
def check_fall(message):
	if str(message.chat.id) in list_chatid[1]:
		#retrieve key from chat_id
		index_key=list_chatid[1].index(str(message.chat.id))
		key=list_chatid[0][index_key]
		bot.reply_to(message,"Loading Fall Prediction...")

		#retrieve results
		graph_direc = server.get_directory(key, "2d_result")
		result_2d = server.retrieve_file_string(graph_direc)
		graph_direc = server.get_directory(key, "3d_result")
		result_3d = server.retrieve_file_string(graph_direc)
		graph_direc = server.get_directory(key, "unconscious_result")
		result_uncon = server.retrieve_file_string(graph_direc)
		graph_direc = server.get_directory(key, "pressure_result")
		result_ps=server.retrieve_file_string(graph_direc)

		#get current time
		now = datetime.now()
		dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

		bot.reply_to(message, "Checking status fall of each sensor:\n\n2D LIDAR ML Prediction: "+result_2d\
					 +"\n3D LIDAR ML Prediction: "+result_3d+"\n3D LIDAR Conscious State: "+result_uncon+"\nPressure Sensor Fall Prediction: "+result_ps \
					 +"\n\nResults taken on: "+dt_string+ " hrs"

					 )
	else:
		markup = types.ReplyKeyboardRemove(selective=False)
		bot.send_message(message.chat.id, "Chat ID not verified.\nError 403: Unauthorised access.", reply_markup=markup)

@bot.message_handler(commands=['microphone'])
def microphone(message):

	if str(message.chat.id) in list_chatid[1]:
		try:
			index_key=list_chatid[1].index(str(message.chat.id))
			key=list_chatid[0][index_key]

			bot.reply_to(message, "Loading microphone data...")
			#item='microphone'
			now = datetime.now()
			dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
			#direc = server.get_directory(key, item)
			#data = server.retrieve_file(direc,"mp3")

			#get mic_cmd status
			item = 'mic_cmd'
			direc = server.get_directory(key, item)
			mic = server.retrieve_file_string(direc)
			mic_cmd = mic.split(',')[0]
			print(mic_cmd)
			if mic_cmd=="False":
				audio_text="This is an audio file for Postal ID "+key+". No fall has been detected yet hence no audio can be provided."
				tts = gtts.gTTS(
					audio_text,
					lang="en")
				tts.save("temp/temp.mp3")
				with open('temp/temp.mp3', 'rb') as file:
					data = file.read()
				mic_text = "Disabled"
			else:
				item = 'microphone'
				direc = server.get_directory(key, item)
				data = server.retrieve_file(direc,"mp3")
				mic_text="Enabled"

				pass
			bot.send_audio(message.chat.id,data,caption="Microphone recording status: "+mic_text+"\nCaptured recordings on:\n"+dt_string+" hrs",title=key+" Recording",performer="ElderILY system")
		except Exception as e:
			error_msg="Error encountered!\n\nError message:\n"+str(e)+"\n\nEnd of error message"
			bot.reply_to(message, error_msg)
			pass
	else:
		markup = types.ReplyKeyboardRemove(selective=False)
		bot.send_message(message.chat.id, "Chat ID not verified.\nError 403: Unauthorised access.", reply_markup=markup)


@bot.message_handler(commands=['2DImageLidar','lidar_2d'])
def image_2d(message):

	if str(message.chat.id) in list_chatid[1]:
		try:
			#load key
			index_key=list_chatid[1].index(str(message.chat.id))
			key=list_chatid[0][index_key]

			bot.reply_to(message, "Loading 2D LIDAR graph...")
			item = "2d lidar"
			img_direc = server.get_directory(key, item)
			data = server.retrieve_img(img_direc)
			graph_direc = server.get_directory(key, "2d_result")
			result_2d = server.retrieve_file_string(graph_direc)

			now = datetime.now()
			dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
			caption="Current 2D image retrieved Date & Time:\n"+dt_string+" hrs\n2D Prediction result: "+ result_2d
			bot.send_photo(message.chat.id,data,caption)
		except Exception as e:
			error_msg = "Error encountered!\n\nError message:\n" + str(e) + "\n\nEnd of error message"
			bot.reply_to(message, error_msg)
			pass
	else:
		markup = types.ReplyKeyboardRemove(selective=False)
		bot.send_message(message.chat.id, "Chat ID not verified.\nError 403: Unauthorised access.", reply_markup=markup)
	pass

@bot.message_handler(commands=['3DImageLidar','lidar_3d'])
def image_3d(message):

	if str(message.chat.id) in list_chatid[1]:
		try:
			bot.reply_to(message, "Loading 3D LIDAR graph...")
			#load key
			index_key=list_chatid[1].index(str(message.chat.id))
			key=list_chatid[0][index_key]

			item = "lidar"
			graph_direc = server.get_directory(key, item)
			data = server.retrieve_file_string(graph_direc)
			res = ast.literal_eval(data)

			x = [x[0] for x in res]
			y = [x[1] for x in res]
			z = [x[2] for x in res]
			fig = go.Figure(data=[go.Scatter3d(
				x=x,
				y=y,
				z=z,
				mode='markers',
				marker=dict(
					size=1.5,
					color=x,  # set color to an array/list of desired values
					colorscale='Viridis',  # choose a colorscale
					opacity=0.8
				)
			)],

			)
			fig.update_layout(template="plotly_dark")
			bot.reply_to(message, "3D LIDAR graph loaded on server.\nPreparing HTML file...")
			test=fig.to_html()

			with open("temp/3D Cloud Point.html", "w",encoding="utf-8") as file:
				file.write(test)
			#plotly.io.write_html(fig,file="graph.html")
			#fig.write_html("graph.html")
			file=open("temp/3D Cloud Point.html", "rb")
				#file.write(graph)

			now = datetime.now()
			dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
			bot.reply_to(message, "HTML file created.\nRetrieving prediction results and sending graph...")
			graph_direc = server.get_directory(key, "3d_result")
			result_3d = server.retrieve_file_string(graph_direc)
			graph_direc = server.get_directory(key, "unconscious_result")
			result_uncon = server.retrieve_file_string(graph_direc)

			bot.send_document(message.chat.id,document=file)

			bot.reply_to(message, "3D Prediction result: "+result_3d+"\n3D LIDAR Conscious State: "+result_uncon+"\nFile sent at: "+dt_string+" hrs")
			file.close()
		except Exception as e:
			error_msg = "Error encountered!\n\nError message:\n" + str(e) + "\n\nEnd of error message"
			bot.reply_to(message, error_msg)
			pass
	else:
		markup = types.ReplyKeyboardRemove(selective=False)
		bot.send_message(message.chat.id, "Chat ID not verified.\nError 403: Unauthorised access.", reply_markup=markup)



@bot.message_handler(commands=['GetElderlyContact','get_elderly_contact'])
def get_contact(message):

	if str(message.chat.id) in list_chatid[1]:
		try:
		#load key
			index_key=list_chatid[1].index(str(message.chat.id))
			key=list_chatid[0][index_key]

			bot.reply_to(message, "Getting elderly Bio details...")
			lat,lon,details=retrieve_details(key)
			bot.reply_to(message, "Sending Elderly location:")
			bot.send_location(message.chat.id,float(lat),float(lon))
			now = datetime.now()
			dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
			bot.reply_to(message, "Elderly details are as follow:\n\n"+details+"\n\nGenerated on: "+dt_string+" hrs")
		except Exception as e:
			error_msg = "Error encountered!\n\nError message:\n" + str(e) + "\n\nEnd of error message"
			bot.reply_to(message, error_msg)
			pass
	else:
		markup = types.ReplyKeyboardRemove(selective=False)
		bot.send_message(message.chat.id, "Chat ID not verified.\nError 403: Unauthorised access.", reply_markup=markup)


@bot.message_handler(commands=['PressureGraph','pressure_graph'])
def p_graph(message):

	if str(message.chat.id) not in list_chatid[1]:
		markup = types.ReplyKeyboardRemove(selective=False)
		bot.send_message(message.chat.id, "Chat ID not verified.\nError 403: Unauthorised access.", reply_markup=markup)
		return
	try:
		# load key
		index_key = list_chatid[1].index(str(message.chat.id))
		key = list_chatid[0][index_key]

		bot.reply_to(message, "Retrieving Pressure data and converting into graph...")
		item = "pressure_data_1000"
		direc = server.get_directory(key, item)
		graph_direc = server.get_directory(key, "pressure_result")
		result_ps = server.retrieve_file_string(graph_direc)

		data = server.retrieve_file_string(direc)
		ver1 = data.split('\n')
		p_data = [i.split(",") for i in ver1 if len(i) > 1]
		fall_index=[]
		for index,row_data in enumerate(p_data):
			#print(row_data)
			check_row = ''.join(row_data)
			if check_row.isalpha() or len(row_data) < 4:
				p_data[index]=[0,0,0,0]

			if ' Fall detected' in row_data:
				#print("fall detected at:",index)
				fall_index.append(index)


		x_range=[i for i in range(len(p_data))]
		fig = make_subplots(rows=1, cols=1)




		fig.add_trace(go.Scatter(
			y=[float(i[1]) for i in p_data],
			x=x_range,

			mode='lines',
			marker=dict(
				size=3,
				colorscale='Viridis',  # choose a colorscale
				opacity=0.8
			),

			name="Tile 1"), row=1, col=1

		)
		fig.add_trace(go.Scatter(
			y=[float(i[2])  for i in p_data],
			x=x_range,

			mode='lines',
			marker=dict(
				size=3,
				colorscale='Viridis',  # choose a colorscale
				opacity=0.8
			),

			name="Tile 2"), row=1, col=1

		)
		fig.add_trace(go.Scatter(
			y=[float(i[3])  for i in p_data],
			x=x_range,

			mode='lines',
			marker=dict(
				size=3,
				colorscale='Viridis',  # choose a colorscale
				opacity=0.8
			),

			name="Tile 3"), row=1, col=1

		)

		for fall_xvalue in fall_index:
			fig.add_vrect(x0=fall_xvalue-10, x1=fall_xvalue,
									   annotation_text="Fall Detected", annotation_position="top left",
									 fillcolor="red", opacity=0.25, line_width=0)


		fig.update_xaxes(nticks=20)
		fig.update_layout(template="plotly_dark",width=1600,height=900,title="Weight(Kg) against time(s) graph",title_x=0.5)
		fig.update_xaxes(title_text="Seconds(s)")
		fig.update_yaxes(title_text="Weight(Kg)", range=[0, 120])

		fig.write_image("temp/pressure_data.jpeg")
		#open file
		now = datetime.now()
		dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
		file = open("temp/pressure_data.jpeg", "rb")

		bot.send_photo(message.chat.id,file)
		bot.reply_to(message, "Pressure tile Prediction result: " + result_ps + "\nFile sent at: " + dt_string + " hrs")
	except Exception as e:
		error_msg="Error encountered!\n\nError message:\n"+str(e)+"\n\nEnd of error message"
		bot.reply_to(message, error_msg)
		pass


@bot.message_handler(commands=['cancel','c'])
def clear_keyboard(message):
	markup = types.ReplyKeyboardRemove(selective=False)
	bot.send_message(message.chat.id, "Clearing keyboard. Type in /start to begin.", reply_markup=markup)

@bot.message_handler(commands=['acknowledge'])
def acknowledge_fall(message):
	#verify checkid
	if str(message.chat.id) not in list_chatid[1]:
		markup = types.ReplyKeyboardRemove(selective=False)
		bot.send_message(message.chat.id, "Chat ID not verified.\nError 403: Unauthorised access.", reply_markup=markup)
		return
	#This function will upload the acknowledgement into True/False,<Time> in GCP
	#Snooze function will be 10 mins, if the fall detection is still positive, it will ring again after 10 mins
	bot.reply_to(message, "Acknowledging alarm, please wait....")

	#Retrieve time details
	now = datetime.now()
	dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

	#Retrieve key and chatID details
	key_index=list_chatid[1].index(str(message.chat.id))
	key=list_chatid[0][key_index]

	#upload acknowledgement
	directory = server.get_directory(key, "acknowledge")
	#ack = server.retrieve_file_string(directory)
	#ack = ack.split(',')
	#if ack[0]==False:
	#	text = "No acknowledgement needs to be done.Revert back to main menu."
	#	bot.reply_to(message, text)
	#	return

	server.upload_string(directory,"True,"+dt_string)

	text="Fall acknowledged at "+dt_string+"hrs.\n"
	text=text+"In the event the fall is not cleared or detected, the next Fall alarm will be in 10 minutes. However, if the priority changes, the alarm will be sent once."
	bot.reply_to(message,text)

@bot.message_handler(commands=['UpdateChatID','update_chat_id'])
def update_chatID(message):
	bot.reply_to(message, "Please standby postal code + unit number for this verification. 2FA will be used on ElderILY dashboard.")
	postal=bot.reply_to(message,"Please enter unique ID for the unit that you will be receiving alerts from:")
	bot.register_next_step_handler(postal,verify_postal)

def verify_postal(message):
	chatid=message.chat.id
	unique_id=message.text
	bot.send_message(chatid,"Verifying unique ID '"+unique_id+"' ...")

	postal=list_chatid[0]
	if unique_id in postal:
		bot.reply_to(message, "Unique ID verified!")
		print("Generating random no")
		encrypt_no=random.randint(100000,999999)
		item = "True,"+str(encrypt_no)+","+unique_id
		print("Uploading string")
		server.upload_string("telebot_2FA.txt",item)
		bot.send_message(chatid, "A 6 digit code has been sent to ElderILY dashboard home. Click on 'Generate 2FA for chat ID' to retrieve.")
		code= bot.reply_to(message,"Please enter the 6 digit code:")
		bot.register_next_step_handler(code,verify_pin)
		#server.upload_string("telebot_2FA.txt", "False")
	else:
		bot.reply_to(message, "Unique ID not verified! Reverting to main program.")
		server.upload_string("telebot_2FA.txt", "False")

def verify_pin(message):
	print("Current chatID:", list_chatid)
	pin=message.text
	chatid=message.chat.id
	item=server.retrieve_file_string("telebot_2FA.txt")
	item=item.split(',')
	actual_pin=item[1]
	if actual_pin==pin:
		bot.reply_to(message, "Pin verified! Updating ChatID into ElderILY database.")
		direc_item = "details"
		detail_direc = server.get_directory(item[2], direc_item)
		data = server.retrieve_file_string(detail_direc)
		res = ast.literal_eval(data)

		res['bio']['caretaker']['chat_ID'] = chatid
		res['bio']['caretaker']['name'] = message.from_user.first_name+' '+ message.from_user.last_name
		res['bio']['caretaker']['tele'] = '@'+ message.from_user.username
		server.upload_string(detail_direc, str(res))
		bot.send_message(chatid,"ChatID updated!")
		#list_chatid.append(str(chatid))
		for count,stuff in enumerate(list_chatid[0]):
			if stuff==item[2]:
				list_chatid[1][count]=str(chatid)
		print("Updated chatID:",list_chatid)
		text="You will now be able to receive alerts from ElderILY on postal code: "+item[2]+"\nTo get started, the elderly you are assigned will be displayed below."
		bot.send_message(chatid, text)

		get_contact(message)
	else:
		bot.reply_to(message, "Unique ID not verified! Reverting to main program.")

	server.upload_string("telebot_2FA.txt", "False")


#retrieve from https://lavrynenko.com/en/python-telebot-get-user-phone-number/
@bot.message_handler (commands = ['contact']) # Announced a branch in which we prescribe logic in case the user decides to send a phone number :)
def contact (message):
	print(message.from_user.id, message.from_user.first_name, message.from_user.last_name, message.from_user.username)
	bot.reply_to(message, "Contact:"+str(message.from_user.id)+"|"+ message.from_user.first_name+'|'+ message.from_user.last_name+"|"+ message.from_user.username)
def retrieve_details(key):

	#Retrieving data for unit
	unit = server.retrieve_file_string("unit_location.txt")
	data = unit.split("\r\n")
	unit_data = [i.split(",") for i in data if len(i) > 1]
	unit_details = []

	for item in unit_data:
		if item[3]==key:
			unit_details=item


	#retrieving elderly details
	direc_item = "details"
	detail_direc = server.get_directory(key, direc_item)
	data = server.retrieve_file_string(detail_direc)
	res = ast.literal_eval(data)
	e_blk="Block no: "+ item[1]
	e_unit="Unit no: "+item[2]
	e_lat=item[4]
	e_lon=item[5]
	#Simulation medical illness
	medical_history="Unknown"
	#formating elderly names into string
	e_name="Elderly name: " + res['bio']['elderly']['Name']
	e_age="Elderly age: " +str(res['bio']['elderly']['Age'])
	try:
		e_medical="Elderly known medical History: "+ res['bio']['elderly']['medical']
	except:
		e_medical = "Elderly known medical History: " + medical_history
	return e_lat,e_lon,e_blk+"\n"+e_unit+"\n"+"\n"+e_name+"\n"+e_age+"\n"+e_medical


def state_check(no):
	if no==1:
		return "Running"
	elif no==2:
		return 'Paused'
	elif no==0:
		return 'Stopped'
	else:
		return "Unknown"

@bot.message_handler (commands = ['pauseJob'])
def pause_schedule(message):
	text='Developer command. Pausing job.'
	bot.reply_to(message, text)
	scheduler.pause()
	job=str(scheduler.get_jobs())
	message_text="Current job in queue:\n\n"+job+'\nJob state:'+state_check(scheduler.state)+'\n\nEnd of job state'
	bot.reply_to(message, message_text)

@bot.message_handler (commands = ['startJob'])
def resume_schedule(message):
	text='Developer command. Starting job.'
	bot.reply_to(message, text)
	scheduler.resume()
	job=str(scheduler.get_jobs())
	message_text="Current job in queue:\n\n"+job+'\nJob state:'+state_check(scheduler.state)+'\n\nEnd of job state'
	bot.reply_to(message, message_text)


@bot.message_handler(commands=['job'])
def pause_schedule(message):
	job = str(scheduler.get_jobs())
	message_text = "Current job in queue:\n\n" + job + '\nJob state:' + state_check(scheduler.state) + '\n\nEnd of job state'
	bot.reply_to(message, message_text)


@bot.message_handler(func=lambda message: True)
def echo_all(message):

	bot.reply_to(message, message.text)

#begin schedule job
scheduler.start()
print("Scheduling job added")
#jobs=scheduler.state()
print(scheduler.state)
#begin telebot polling
print("Starting TeleBot")
bot.infinity_polling()
print("TeleBot ended")