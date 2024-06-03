from PIL import Image, ImageSequence
import imageio

def crop_gif(input_path, output_path, crop_size=(320, 320)):
    # Open the original GIF
    with Image.open(input_path) as img:
        frames = []
        # Calculate the coordinates to crop the central region
        center_x, center_y = img.width // 2, img.height // 2
        left = center_x - crop_size[0] // 2
        upper = center_y - crop_size[1] // 2 -10
        right = left + crop_size[0]
        lower = upper + crop_size[1] - 10
        
        # Iterate through each frame in the GIF
        for frame in ImageSequence.Iterator(img):
            # Crop the frame
            cropped_frame = frame.crop((left, upper, right, lower))
            frames.append(cropped_frame)
        
        # Save the cropped frames as a new GIF
        frames[0].save(output_path, save_all=True, append_images=frames[1:], loop=0)

# Usage
input_gif = 'static/helper_rb.gif'
output_gif = 'static/helper_rb_crop.gif'
crop_gif(input_gif, output_gif)