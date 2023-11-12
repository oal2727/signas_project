def detect_objects(image_path):
    network, class_names, class_colors = load_network(
        "/mnt/c/Users/Maria/Desktop/tesisjota/ProyectoWeb/parameters/yolov4-custom.cfg",
        "/mnt/c/Users/Maria/Desktop/tesisjota/ProyectoWeb/parameters/obj.data",
        "/mnt/c/Users/Maria/Desktop/tesisjota/ProyectoWeb/parameters/yolov4-custom_last_4300.weights",
        batch_size=1
    )
    width = network_width(network)
    height = network_height(network)
    image = cv2.imread(image_path)
    darknet_image = make_image(network_width(network), network_height(network), 3)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image_resized = cv2.resize(image_rgb, (width, height),
                               interpolation=cv2.INTER_LINEAR)
    copy_image_from_bytes(darknet_image, image_resized.tobytes())
    detections = detect_image(network, class_names, darknet_image)
    free_image(darknet_image)
    image_final = draw_boxes(detections, image_resized, class_colors)
    # draw_boxes(image,detections)
    return cv2.cvtColor(image_final, cv2.COLOR_BGR2RGB), detections,class_names


image, detections,class_names = detect_objects(image_path) # deteccion de objetos 
cv2.imwrite("file.jpg",frame)
