import cv2
import requests
import threading

# URL API untuk upload gambar
UPLOAD_URL = "https://078b-103-104-130-40.ngrok-free.app/api/upload-fire-image/"

def upload_image(image_path):
    """Fungsi untuk mengunggah gambar ke API di thread terpisah."""
    try:
        with open(image_path, 'rb') as image_file:
            files = {'fire_image': image_file}
            response = requests.post(UPLOAD_URL, files=files)

            if response.status_code == 201:
                print("Image uploaded successfully!")
                print("Response:", response.json())
            else:
                print(f"Failed to upload image. Status code: {response.status_code}")
                print("Response:", response.text)
    except Exception as e:
        print(f"Error uploading image: {e}")

def main():
    """Fungsi utama untuk membuka kamera dan menangkap gambar."""
    cap = cv2.VideoCapture(0)  # Buka kamera (0 untuk kamera utama)
    
    if not cap.isOpened():
        print("Failed to open camera.")
        return
    
    print("Press 's' to capture and upload an image, 'q' to quit.")

    while True:
        ret, frame = cap.read()  # Baca frame dari kamera
        
        if not ret:
            print("Failed to capture frame.")
            break
        
        # Tampilkan frame di jendela
        cv2.imshow('Camera', frame)
        
        # Tunggu input dari keyboard
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('s'):  # Jika tombol 's' ditekan
            # Simpan gambar sementara ke disk
            image_path = "captured_image.jpg"
            cv2.imwrite(image_path, frame)
            print(f"Image saved to {image_path}. Uploading...")

            # Jalankan upload di thread terpisah
            threading.Thread(target=upload_image, args=(image_path,)).start()
        
        elif key == ord('q'):  # Jika tombol 'q' ditekan
            print("Exiting...")
            break
    
    # Tutup kamera dan jendela
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
