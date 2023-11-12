detections, width_ratio, height_ratio = detected.darknet_helper(frame) # paso 2 obtener array de deteccion
# paso 3 asignar el cuadro delimitador a la matriz negra
for label, confidence, bbox in detections:
    left, top, right, bottom = bbox2points(bbox)
    left, top, right, bottom = int(left * width_ratio), int(top * height_ratio), int(right * width_ratio), int(bottom * height_ratio)
    bbox_array = cv2.rectangle(bbox_array, (left, top), (right, bottom), detected.colors[label], 2)
    bbox_array = cv2.putText(bbox_array, "{} [{:.2f}]".format(label, float(confidence)),
        (left, top - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
        detected.colors[label], 2)
    bbox_array[:, :, 3] = (bbox_array.max(axis=2) > 0).astype(int) * 255 # Paso 4 . Este fragmento calcula el valor máximo a lo largo del eje de los canales de color
    result = frame.copy() # paso 5 . crear una copia de la imagen original
# paso 6 . asigna los valores de los canales RGB de bbox_array (para los píxeles que tienen algún color) a los píxeles correspondientes en la imagen
result[bbox_array[:, :, 3] > 0] = bbox_array[:, :, :3][bbox_array[:, :, 3] > 0] # 
#    data_test,draw_image_array,data_check,tiempo_detectado_letra,array_image,tiempo_inicio_array = detected.validate_label(label,total_general,directorySave,result,data_test,draw_image_array,data_check,tiempo_detectado_letra,array_image,tiempo_inicio_array)
# if len(data_check) == TOTAL_DE_CARACTERES_ACERTAR:
# print(f"FELICIDADES GANASTE {nombre_persona} ")
# break
# paso 7 . convertir la imagen a base64
bbox = detected.bbox_to_bytes(bbox_array)