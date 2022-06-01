"""
        _                                                              
       (_)                                                             
  _ __  _ _ __ _   _  ___    _ __  _ __ ___   __ _ _ __ __ _ _ __ ___  
 | '_ \| | '__| | | |/ _ \  | '_ \| '__/ _ \ / _` | '__/ _` | '_ ` _ \ 
 | | | | | |  | |_| | (_) | | |_) | | | (_) | (_| | | | (_| | | | | | |
 |_| |_|_|_|   \__, |\___/  | .__/|_|  \___/ \__, |_|  \__,_|_| |_| |_|
                __/ |       | |               __/ |                    
               |___/        |_|              |___/                     

"""

""" VERSIONE CON LA CORREZIONE NEL CASO L'UTENTE BARI E I MICROBIT PER LA COMUNICAZIONE DEL PULSANTE
PREMUTO"""

# |..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..| #
" LIBRERIE "

import imutils
import cv2
import numpy as np
from pathlib import Path
from pyniryo import *
from time import sleep
from tic_tac_toe import GameController
from easyAI import TwoPlayersGame, AI_Player, Negamax
from easyAI.Player import Human_Player
from copy import deepcopy

# |..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..| #
" INSTALLAZIONE LIBRERIE NON NATIVE "

# --> pip install imutils <--

# |..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..| #
" COSTANTI e VARIABILI GLOBALI "
# 0 verde, 1 arancione
colore_robot = 0
colore_giocatore = 1
AREA_MINIMA_FIGURA = 1500
INIZIO_UMANO = 1
INIZIO_ROBOT = 2
FINE_GIOCO = "Partita finita"
PIN_PULSANTE = '2A'

HEIGHT_OFFSET = 0.002
MIN_GRANDEZZA_FACCIA = 10000

dir_path = str(Path(__file__).parent.resolve())

#il minimo e il massimo del colore VERDE e ARANCIONE in formato HSV
boundaries = [ (0, [38, 43, 31], [113, 255, 255]), (1, [5, 191, 78], [179, 255, 255])]
matrice = [[None for _ in range(3)] for _ in range(3)]

# Load the cascade
face_cascade = cv2.CascadeClassifier(f'{dir_path}/faceDetector/haarcascade_frontalface_default.xml')
# Read the input image
font = cv2.FONT_HERSHEY_SIMPLEX
fontScale = 2
fontColor = (0,0,255)

#variabili globali per l'oggetto Niryo
robot_ip_address = "10.10.10.10"
robot = NiryoRobot(robot_ip_address)

robot.update_tool()
robot.set_pin_mode(PIN_PULSANTE,PinMode(1)) #0: OUPUT, 1:INPUT

obj_pose_workspace_destra = PoseObject(-0.001, -0.171, 0.344, 0.457, 1.495, -1.219)
obj_pose_workspace_dritto = PoseObject(0.177, 0.036, 0.329, -2.991, 1.523, -3.103)
obj_pose_workspace_centro = PoseObject(0.145, -0.199, 0.324, 0.042, 1.474, -0.125)
partita_finita_1 = PoseObject(0.109, 0.162, 0.038, -0.012, -0.027, 0.819)
partita_finita_2 = PoseObject(0.133, -0.148, 0.041, 0.011, -0.076, -0.939)
posa_foto = PoseObject(0.146, -0.009, 0.209, 0.074, -0.105, -0.099) 

robot.move_pose(obj_pose_workspace_dritto)
robot.close_gripper(speed=100)

# |..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..| #
" FUNZIONI "

def main():
	global matrice
	global colore_robot

	robot.open_gripper(speed=100)

	colore_robot = scegli_colore()
	g_iniziale = chi_inizia()
	prima_volta = True
	
	algorithm = Negamax(2) # 7 (imbattibile)
	gioco_tris = GameController([Human_Player(), AI_Player(algorithm)], g_iniziale)
	

	while True:
		nuova_matrice, w, h = processing_image_workspace_dritto()
		n_diff, differenze = check_differences(matrice, nuova_matrice)

		if prima_volta and g_iniziale == INIZIO_ROBOT:
			if n_diff == 0:
				prima_volta = False
				mossa_robot = gioco_tris.inizio_mossa_robot()

				if  mossa_robot != None:
					mb = mossa_robot-1
					x = mb%3
					y = (mb-mb%3)//3
					matrice[y][x] = (mossa_robot, colore_robot)
					#print(f"mossa robot: {matrice}")
					muovi_robot(float((x*w/3)+w/6)/w, float((y*h/3)+h/6)/h)

			else: 
				check_baro(matrice, nuova_matrice, w, h)
				print("Sembra ci siano già dei blocchetti!\nTi ricordo che 'Soddisfa più una sconfitta pulita dove hai dato tutto, \npiuttosto che una vittoria ottenuta barando.'\n\t- Jury Chechi\nRimetti i cubetti correttamente")
		else:
			#print(f"nuova matrice robot: {nuova_matrice}")
			if n_diff == 0: print("Devi ancora fare la tua mossa!")
			elif n_diff > 1:
				print("Sembra che tu abbia spostato i blocchetti!\nTi ricordo che 'Soddisfa più una sconfitta pulita dove hai dato tutto, \npiuttosto che una vittoria ottenuta barando.'\n\t- Jury Chechi\nRimetti i cubetti correttamente")
				check_baro(matrice, nuova_matrice, w, h)
			else:
				matrice = deepcopy(nuova_matrice)
				print("Sto per fare la mia mossa!")
				# sleep(2)
				# INVIO LA MOSSA DELL'UTENTE E SALVO QUELLA DEL ROBOT NELLA MATRICE #
				#mossa = int(input("mossa: ")) #da modificare
				mossa_robot = gioco_tris.play(differenze[0][0])
				if FINE_GIOCO not in str(mossa_robot):
					mb = mossa_robot-1
					x = mb%3
					y = (mb-mb%3)//3
					matrice[y][x] = (mossa_robot, colore_robot)
					#print(f"mossa robot: {matrice}")
					muovi_robot(float((x*w/3)+w/6)/w, float((y*h/3)+h/6)/h)
				# ---------------------------------------------------------------- #

				# CONTROLLO CHE LA PARTITA SIA FINITA #
				isover, vincitore = gioco_tris.is_over_2()
				if isover:
					#chi inizia è anche chi ha finito la partita, ma l'ultima parte 
					#della funzione play cambia il giocatore quindi si intende quello opposto
					# a chi ha iniziato
					print(vincitore)

					if "Ho vinto" in vincitore:
						robot.move_pose(posa_foto)
						mostra_risultato()
						sleep(3)
						
					robot.move_pose(partita_finita_1)
					robot.move_pose(partita_finita_2)
					sleep(1)
					robot.move_pose(obj_pose_workspace_dritto)
				
					break
				# ---------------------------------- #
		print("Premere il pulsante dopo aver effettuato la mossa!")
		while robot.digital_read(PIN_PULSANTE) != PinState.HIGH: pass  #LOW:False, HIGH: True
		

def chi_inizia():
	while True:
		opzione = input("Inizia il robot o l'umano? (robot/umano): ")
		if opzione.lower() == "robot": return INIZIO_ROBOT
		elif opzione.lower() == "umano": return INIZIO_UMANO
		print("Opzione non valida!\n")

def scegli_colore():
	while True:
		opzione = input("Vuoi i cubetti verdi o arancioni? (verde/arancione): ")
		if opzione.lower() == "verde": return 1
		elif opzione.lower() == "arancione": return 0
		print("Opzione non valida!\n")
	

def save_image(nome_immagine='immagine.jpeg'):
	immagine_scattata = robot.get_img_compressed()
	with open(f"{dir_path}/{nome_immagine}", "wb") as img: img.write(immagine_scattata)


def verifica_correttezza_immagine():
	save_image()
	image_read = cv2.imread(f"{dir_path}/immagine.jpeg")
	image_read = extract_img_workspace(image_read)
	try:
		h,w,c = image_read.shape
		return image_read,h,w,c
	except:
		print("Non è stato possibile estrarre il workspace dall'immagine")
		sleep(2)
		return verifica_correttezza_immagine()

def processing_image_workspace_dritto():
	matrice_foto = [[None for _ in range(3)] for _ in range(3)]

	sleep(1)
	
	image_read,h,w,_ = verifica_correttezza_immagine()
	
	"""cv2.imshow("immagine_estratta", image_read)
	cv2.waitKey(0)"""

	for (id_colore, lower, upper) in boundaries:

		# FILTRO PER COLORE #
		image = cv2.cvtColor(image_read, cv2.COLOR_BGR2HSV)
		mask = cv2.inRange(image, np.array(lower), np.array(upper))
		output = cv2.bitwise_and(image, image, mask = mask)
		"""cv2.imshow("CONVERSIONE", output)
		cv2.waitKey(0)"""
		# ------------------ #

		# FILTRO GRIGIO E TRASFORMAZIONE DELL'IMMAGINE IN BIANCO E NERO #
		gray = cv2.cvtColor(cv2.cvtColor(output, cv2.COLOR_HSV2BGR), cv2.COLOR_BGR2GRAY)
		blurred = cv2.GaussianBlur(gray, (5, 5), 0)
		thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY)[1]
		"""cv2.imshow("THREASH", thresh)
		cv2.waitKey(0)"""
		# -------------------------------------------------------------------------- #

		# TROVARE I CONTORNI #
		cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
		cnts = imutils.grab_contours(cnts)
		# ------------------ #

		# TROVARE I CENTRI DEI CONTORNI #
		for c in cnts:
			# verifichiamo l'area della figura
			area = cv2.contourArea(c)
			angle = cv2.minAreaRect(c)[2]

			if area > AREA_MINIMA_FIGURA:
				M = cv2.moments(c)
				cX = int(M["m10"] / M["m00"])
				cY = int(M["m01"] / M["m00"])
				#print(f"Contorni dell'immagine: X→ {cX}, Y→ {cY}")
				# draw the contour and center of the shape on the image
				"""cv2.drawContours(output, [c], -1, (0, 255, 0), 2)
				cv2.circle(output, (cX, cY), 7, (255, 255, 255), -1)
				cv2.putText(output, "center", (cX - 20, cY - 20),
				cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
				cv2.imshow("Image", output)
				cv2.waitKey(0)"""

				matrice_foto[int(cY/(h/3))][int(cX/(w/3))] = (int(cY/(h/3))*3 + int(cX/(w/3)) + 1, id_colore, angle)
		# ---------------------------- #
	return matrice_foto, w, h



def processing_image_workspace_blocchi(isHumanWorkspace=False):

	sleep(1)
	image_read,h,w,_ = verifica_correttezza_immagine()
	
	"""cv2.imshow("immagine_estratta", image_read)
	cv2.waitKey(0)"""

	# CONTROLLO QUAL'È IL COLORE DEI CUBETTI DEL ROBOT #
	boundaries_robot = boundaries[1]
	if colore_robot == boundaries[0][0]: boundaries_robot = boundaries[0]
	
	if isHumanWorkspace:
		if colore_robot == boundaries[0][0]: boundaries_robot = boundaries[1]
		else: boundaries_robot = boundaries[0]
	# ------------------------------------------------ #

	# FILTRO PER COLORE #
	image = cv2.cvtColor(image_read, cv2.COLOR_BGR2HSV)
	mask = cv2.inRange(image, np.array(boundaries_robot[1]), np.array((boundaries_robot[2])))
	output = cv2.bitwise_and(image, image, mask = mask)
	"""cv2.imshow("CONVERSIONE", output)
	cv2.waitKey(0)"""
	# ------------------ #

	# FILTRO GRIGIO E TRASFORMAZIONE DELL'IMMAGINE IN BIANCO E NERO #
	gray = cv2.cvtColor(cv2.cvtColor(output, cv2.COLOR_HSV2BGR), cv2.COLOR_BGR2GRAY)
	blurred = cv2.GaussianBlur(gray, (5, 5), 0)
	thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY)[1]
	"""cv2.imshow("THREASH", thresh)
	cv2.waitKey(0)"""
	# -------------------------------------------------------------------------- #

	# TROVARE I CONTORNI #
	cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	cnts = imutils.grab_contours(cnts)
	# ------------------ #

	# TROVARE I CENTRI DEL PRIMO CONTORNO #
	if cnts == []: return "", "", "", "ERRORE! Non riesco a trovare dei cubetti"


	for cnt in cnts:
		# verifichiamo l'area della figura
		area = cv2.contourArea(cnt)
		#trovo l'angolo
		angle = cv2.minAreaRect(cnt)[2]
		if area > AREA_MINIMA_FIGURA:
			M = cv2.moments(cnt)
			cX = int(M["m10"] / M["m00"])
			cY = int(M["m01"] / M["m00"])
			#print(f"Contorni dell'immagine: X→ {cX}, Y→ {cY}")
			# draw the contour and center of the shape on the image
			"""cv2.drawContours(output, [cnt], -1, (0, 255, 0), 2)
			cv2.circle(output, (cX, cY), 7, (255, 255, 255), -1)
			cv2.putText(output, "center", (cX - 20, cY - 20),
			cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
			cv2.imshow("Image", output)
			cv2.waitKey(0)"""
			# conversione da pixel a percentuale workspace
			return (float(cX) / w), (float(cY) / h), angle, "OK"
		
	return "", "", "", "ERRORE! Non riesco a trovare dei cubetti"
	# ---------------------------- #
	
	
	
def check_differences(matrice_precedente, matrice_attuale):
	n_differenze = 0
	elementi_differenti = []

	print(f"Matrice vecchia: {matrice_precedente}")
	print(f"Matrice nuova: {matrice_attuale}")

	for y1, y2 in zip(matrice_precedente, matrice_attuale):
		for x1, x2 in zip(y1, y2):
			
			#parte aggiunta adesso

			if x1 != None:
				x1 = x1[0:2]
			if x2 != None:
				x2 = x2[0:2]
				
			if x1 != x2:
				n_differenze += 1
				if x2[1] == colore_robot: n_differenze +=100
				elementi_differenti.append(x2)
				if x1 != None: n_differenze +=100

	return n_differenze, elementi_differenti

def check_baro(matrice_precedente, matrice_attuale, w, h):
	for y1, y2 in zip(matrice_precedente, matrice_attuale):
		for x1, x2 in zip(y1, y2):
			if x2 != None: 
				angolo_x2 = x2[2]
				x2 = x2[0:2]

			if x1 != None and len(x1) == 3: x1 = x1[0:2]
			print(f"x1: {x1} - x2: {x2}")
			if x1 != x2:
				if x1 != None:
					mb = x1[0]-1
					x = mb%3
					y = (mb-mb%3)//3
					if x2 == None:
						if x1[1] == colore_robot: muovi_robot(float((x*w/3)+w/6)/w, float((y*h/3)+h/6)/h)
						else: muovi_robot(float((x*w/3)+w/6)/w, float((y*h/3)+h/6)/h, "workspace_centro", obj_pose_workspace_centro, isHumanWorkspace=True)
					else:
						if x2[1] == colore_robot: 
							muovi_robot_contrario(float((x*w/3)+w/6)/w, float((y*h/3)+h/6)/h, angolo_x2)
							muovi_robot(float((x*w/3)+w/6)/w, float((y*h/3)+h/6)/h, "workspace_centro", obj_pose_workspace_centro, isHumanWorkspace=True)
						else: 
							muovi_robot_contrario(float((x*w/3)+w/6)/w, float((y*h/3)+h/6)/h, angolo_x2, "workspace_centro", obj_pose_workspace_centro)
							muovi_robot(float((x*w/3)+w/6)/w, float((y*h/3)+h/6)/h, isHumanWorkspace=False)
				else:
					mb = x2[0]-1
					x = mb%3
					y = (mb-mb%3)//3
					if x2[1] == colore_robot: muovi_robot_contrario(float((x*w/3)+w/6)/w, float((y*h/3)+h/6)/h, angolo_x2)
					else: muovi_robot_contrario(float((x*w/3)+w/6)/w, float((y*h/3)+h/6)/h, angolo_x2, "workspace_centro", obj_pose_workspace_centro)
				

def muovi_robot(x_rel, y_rel, workspace="workspace_destra", obs_pose=obj_pose_workspace_destra, isHumanWorkspace=False):
	yaw_rel = 0
	#print(f"Coordinate: {x_rel}-{y_rel}")

	robot.move_pose(obs_pose)
	sleep(2)
	x_rel_dx, y_rel_dx, angolo, errore = processing_image_workspace_blocchi(isHumanWorkspace=isHumanWorkspace)
	if "ERRORE" in errore: 
		print(errore)
		exit()
	#manca il movimento per girare la pinza di angolo
	robot.open_gripper(speed=100)
	sleep(1)
	pos_robot = robot.get_target_pose_from_rel(workspace, HEIGHT_OFFSET, x_rel_dx, y_rel_dx, angolo*np.pi/180)
	robot.move_pose(pos_robot)
	#sleep(1)
	robot.close_gripper(speed=100)
	sleep(1)
	robot.move_pose(obs_pose)
	#sleep(1)
	# POSA IL CUBETTO NELLA CELLA DEL WORKSPACE, APRE LA PINZA E TORNA NELLA POSA DI OSSERVAZIONE #
	robot.move_pose(obj_pose_workspace_dritto)
	#sleep(1)
	pos_robot = robot.get_target_pose_from_rel("workspace_dritto", HEIGHT_OFFSET, x_rel, y_rel, 0)
	robot.move_pose(pos_robot)
	#sleep(1)
	robot.open_gripper(speed=100)
	sleep(1)
	robot.move_pose(obj_pose_workspace_dritto)
	#sleep(1)
	robot.close_gripper(speed=100)
	sleep(2)
	# ------------------------------------------------------------------------------------------- #

def muovi_robot_contrario(x_rel, y_rel, angolo, workspace="workspace_destra", obs_pose=obj_pose_workspace_destra):
	robot.move_pose(obj_pose_workspace_dritto)
	robot.open_gripper(speed=100)
	sleep(1)
	pos_robot = robot.get_target_pose_from_rel("workspace_dritto", HEIGHT_OFFSET, x_rel, y_rel, angolo*np.pi/180)
	robot.move_pose(pos_robot)
	robot.close_gripper(speed=100)
	sleep(2)
	robot.move_pose(obj_pose_workspace_dritto)
	robot.move_pose(obs_pose)
	
	#calcolo delle coordinate


	matrice_foto = [[None for _ in range(3)] for _ in range(3)]
	sleep(1)
	image_read,h,w,_ = verifica_correttezza_immagine()
	
	"""cv2.imshow("immagine_estratta", image_read)
	cv2.waitKey(0)"""

	for (id_colore, lower, upper) in boundaries:

		# FILTRO PER COLORE #
		image = cv2.cvtColor(image_read, cv2.COLOR_BGR2HSV)
		mask = cv2.inRange(image, np.array(lower), np.array(upper))
		output = cv2.bitwise_and(image, image, mask = mask)
		"""cv2.imshow("CONVERSIONE", output)
		cv2.waitKey(0)"""
		# ------------------ #

		# FILTRO GRIGIO E TRASFORMAZIONE DELL'IMMAGINE IN BIANCO E NERO #
		gray = cv2.cvtColor(cv2.cvtColor(output, cv2.COLOR_HSV2BGR), cv2.COLOR_BGR2GRAY)
		blurred = cv2.GaussianBlur(gray, (5, 5), 0)
		thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY)[1]
		"""cv2.imshow("THREASH", thresh)
		cv2.waitKey(0)"""
		# -------------------------------------------------------------------------- #

		# TROVARE I CONTORNI #
		cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
		cnts = imutils.grab_contours(cnts)
		# ------------------ #

		# TROVARE I CENTRI DEI CONTORNI #
		for c in cnts:
			# verifichiamo l'area della figura
			area = cv2.contourArea(c)
			angle = cv2.minAreaRect(c)[2]

			if area > AREA_MINIMA_FIGURA:
				M = cv2.moments(c)
				cX = int(M["m10"] / M["m00"])
				cY = int(M["m01"] / M["m00"])
				#print(f"Contorni dell'immagine: X→ {cX}, Y→ {cY}")
				# draw the contour and center of the shape on the image
				"""cv2.drawContours(output, [c], -1, (0, 255, 0), 2)
				cv2.circle(output, (cX, cY), 7, (255, 255, 255), -1)
				cv2.putText(output, "center", (cX - 20, cY - 20),
				cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
				cv2.imshow("Image", output)
				cv2.waitKey(0)"""

				matrice_foto[int(cY/(h/3))][int(cX/(w/3))] = (cX, cY, angle)
		# ---------------------------- #


	ris = -1
	count = 0
	for y in matrice_foto:
		for x in y:
			if x == None:
				ris = count
				break
			count += 1
		
		if ris != -1: break
	if ris == None:
		#nel caso non ci sia spazio lancia il cubo al centro
		pos_robot = robot.get_target_pose_from_rel(workspace, 0.2, 0.5, 0.5, np.pi/180)
	else:
		#mb = mossa_robot-1
		mb = ris
		x = mb%3
		y = (mb-mb%3)//3

		xr = float((x*w/3)+w/6)/w
		yr = float((y*h/3)+h/6)/h
		pos_robot = robot.get_target_pose_from_rel(workspace, HEIGHT_OFFSET, xr, yr, 0)


	# ------------------------------------------
	robot.move_pose(pos_robot)
	robot.open_gripper(speed=100)
	robot.move_pose(obs_pose)
	robot.close_gripper(speed=100)
	robot.move_pose(obj_pose_workspace_dritto)
	# ------------------------------------------------------------------------------------------- #


def mostra_risultato():
	save_image('foto_faccia.jpeg')
	img = cv2.imread(f"{dir_path}/foto_faccia.jpeg")
	# Convert into grayscale
	gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	# Detect faces
	faces = face_cascade.detectMultiScale(gray, 1.1, 4)
	# Draw rectangle around the faces
	if len(faces) == 0:
		img_x, img_y , _ = img.shape
		cv2.putText(img, 'Dove ti sei nascosto??', (int(img_x/7), int(img_y/2)), font, fontScale-1, fontColor, 3,cv2.LINE_AA) 
	else:
		for (x, y, w, h) in faces:
			if w*h > MIN_GRANDEZZA_FACCIA:
				#print(w*h)
				cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
				cv2.putText(img, 'Perdente', (x,y), font, fontScale-1, fontColor, 3,cv2.LINE_AA)
	# Display the output
	cv2.imshow('img', img)
	cv2.waitKey(3000)

# |..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..| #

if __name__ == "__main__":
	main()