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
COLORE_ROBOT = 0
COLORE_GIOCATORE = 1
AREA_MINIMA_FIGURA = 1000
INIZIO_UMANO = 1
INIZIO_ROBOT = 2
FINE_GIOCO = "Partita finita"

HEIGHT_OFFSET = 0.002

dir_path = str(Path(__file__).parent.resolve())

#il minimo e il massimo del colore VERDE e ARANCIONE in formato HSV
boundaries = [ (0, [59, 158, 58], [103, 255, 255]), (1, [3, 220, 122], [179,255,255])]
matrice = [[None for _ in range(3)] for _ in range(3)]

#variabili globali per l'oggetto Niryo
robot_ip_address = "10.10.10.10"
robot = NiryoRobot(robot_ip_address)

robot.update_tool()

obj_pose_workspace_destra = PoseObject(-0.001, -0.191, 0.359, 0.688, 1.49, -1.011)
obj_pose_workspace_dritto = PoseObject(0.158, -0.004, 0.354, 0.677, 1.475, 0.544)
partita_finita_1 = PoseObject(0.109, 0.162, 0.038, -0.012, -0.027, 0.819)
partita_finita_2 = PoseObject(0.133, -0.148, 0.041, 0.011, -0.076, -0.939)

robot.move_pose(obj_pose_workspace_dritto)
robot.close_gripper(speed=100)

# |..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..| #
" FUNZIONI "

def main():
	global matrice

	g_iniziale = chi_inizia()
	prima_volta = True
	
	algorithm = Negamax(7)
	gioco_tris = GameController([Human_Player(), AI_Player(algorithm)], g_iniziale)
	

	while True:
		nuova_matrice, w, h = processing_image_workspace_dritto()
		n_diff, differenze = check_differences(matrice, nuova_matrice)

		if prima_volta:
			prima_volta = False
			mossa_robot = gioco_tris.inizio_mossa_robot()

			if  mossa_robot != None:
				mb = mossa_robot-1
				x = mb%3
				y = (mb-mb%3)//3
				matrice[y][x] = (mossa_robot, COLORE_ROBOT)
				print(f"mossa robot: {matrice}")
				muovi_robot(float((x*w/3)+w/6)/w, float((y*h/3)+h/6)/h)
		else:

			if n_diff == 0: print("Devi ancora fare la tua mossa!")
			elif n_diff > 1:
				print("Sembra che tu abbia spostato i blocchetti!\nTi ricordo che 'Soddisfa più una sconfitta pulita dove hai dato tutto, \npiuttosto che una vittoria ottenuta barando.'\n\t- Jury Chechi\nRimetti i cubetti correttamente")
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
					matrice[y][x] = (mossa_robot, COLORE_ROBOT)
					print(f"mossa robot: {matrice}")
					muovi_robot(float((x*w/3)+w/6)/w, float((y*h/3)+h/6)/h)
				# ---------------------------------------------------------------- #

				# CONTROLLO CHE LA PARTITA SIA FINITA #
				isover, vincitore = gioco_tris.is_over()
				if isover:
					#chi inizia è anche chi ha finito la partita, ma l'ultima parte 
					#della funzione play cambia il giocatore quindi si intende quello opposto
					# a chi ha iniziato
					print(vincitore)
					robot.move_pose(partita_finita_1)
					robot.move_pose(partita_finita_2)
					break
				# ---------------------------------- #
		print("Premere un qualunque tasto dopo aver efffettuato la mossa!")
		#cv2.waitKey(0)
		input('')


def chi_inizia():
	while True:
		opzione = input("Inizia il robot o l'umano? (robot/umano): ")
		if opzione.lower() == "robot": return INIZIO_ROBOT
		elif opzione.lower() == "umano": return INIZIO_UMANO
		print("Opzione non valida!\nInizia il robot o l'umano? (robot/umano): ")

	
	
	

def save_image():
	immagine_scattata = robot.get_img_compressed()
	with open(f"{dir_path}/immagine.jpeg", "wb") as img: img.write(immagine_scattata)

def processing_image_workspace_dritto():
	matrice_foto = [[None for _ in range(3)] for _ in range(3)]

	save_image()
	#image_read = cv2.imread(f"{dir_path}/../immagini_tris/immagine_29.jpeg")
	image_read = cv2.imread(f"{dir_path}/immagine.jpeg")
	image_read = extract_img_workspace(image_read)
	
	h,w,_ = image_read.shape
	
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

				matrice_foto[int(cY/(h/3))][int(cX/(w/3))] = (int(cY/(h/3))*3 + int(cX/(w/3)) + 1, id_colore)
		# ---------------------------- #
	return matrice_foto, w, h


def processing_image_workspace_destra():

	save_image()
	#image_read = cv2.imread(f"{dir_path}/../immagini_tris/immagine_13.jpeg")
	image_read = cv2.imread(f"{dir_path}/immagine.jpeg")
	image_read = extract_img_workspace(image_read)
	
	h,w,_ = image_read.shape
	
	"""cv2.imshow("immagine_estratta", image_read)
	cv2.waitKey(0)"""

	# CONTROLLO QUAL'È IL COLORE DEI CUBETTI DEL ROBOT #
	boundaries_robot = boundaries[1]
	if COLORE_ROBOT == boundaries[0][0]: boundaries_robot = boundaries[0]
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
	if cnts == []: return "ERRORE! Non riesco a trovare dei cubetti" , "", ""

	# verifichiamo l'area della figura
	area = cv2.contourArea(cnts[0])
	#trovo l'angolo
	angle = cv2.minAreaRect(cnts[0])[2]

	if area > AREA_MINIMA_FIGURA:
		M = cv2.moments(cnts[0])
		cX = int(M["m10"] / M["m00"])
		cY = int(M["m01"] / M["m00"])
		#print(f"Contorni dell'immagine: X→ {cX}, Y→ {cY}")
		# draw the contour and center of the shape on the image
		"""cv2.drawContours(output, [cnts[0]], -1, (0, 255, 0), 2)
		cv2.circle(output, (cX, cY), 7, (255, 255, 255), -1)
		cv2.putText(output, "center", (cX - 20, cY - 20),
		cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
		cv2.imshow("Image", output)
		cv2.waitKey(0)"""

	# ---------------------------- #
	
	# conversione da pixel a percentuale workspace
	return (float(cX) / w), (float(cY) / h), angle
		

def check_differences(matrice_precedente, matrice_attuale):
	n_differenze = 0
	elementi_differenti = []

	for y1, y2 in zip(matrice_precedente, matrice_attuale):
		for x1, x2 in zip(y1, y2):
			if x1 != x2:
				n_differenze += 1
				elementi_differenti.append(x2)
			if x1 != None:
				if x2 == None: n_differenze +=100

	return n_differenze, elementi_differenti

def muovi_robot(x_rel, y_rel):
	yaw_rel = 0
	#print(f"Coordinate: {x_rel}-{y_rel}")

	robot.move_pose(obj_pose_workspace_destra)
	x_rel_dx, y_rel_dx, angolo = processing_image_workspace_destra()
	#manca il movimento per girare la pinza di angolo
	robot.open_gripper(speed=100)
	sleep(2)
	pos_robot = robot.get_target_pose_from_rel("workspace_destra", HEIGHT_OFFSET, x_rel_dx, y_rel_dx, angolo*np.pi/180)
	robot.move_pose(pos_robot)
	robot.close_gripper(speed=100)
	sleep(2)
	robot.move_pose(obj_pose_workspace_destra)
	# POSA IL CUBETTO NELLA CELLA DEL WORKSPACE, APRE LA PINZA E TORNA NELLA POSA DI OSSERVAZIONE #
	robot.move_pose(obj_pose_workspace_dritto)
	pos_robot = robot.get_target_pose_from_rel("workspace_dritto", HEIGHT_OFFSET, x_rel, y_rel, 0)
	robot.move_pose(pos_robot)
	robot.open_gripper(speed=100)
	sleep(2)
	robot.move_pose(obj_pose_workspace_dritto)
	robot.close_gripper(speed=100)
	# ------------------------------------------------------------------------------------------- #

# |..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..| #


"""
PER VISUALIZZAR UN IMMAGINE:
cv2.imshow("Image", output)
cv2.waitKey(0)
"""




if __name__ == "__main__":
	main()