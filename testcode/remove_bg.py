from PIL import Image, ImageSequence
from tqdm import tqdm
import os

def make_black_transparent(input_path, output_path):
    # Get the file extension
    ext = os.path.splitext(input_path)[1].lower()
    
    # Open the input image
    img = Image.open(input_path)
    
    if ext == ".gif":
        # Create a list to store the frames
        frames = []

        # Get the total number of frames
        total_frames = img.n_frames

        # Iterate through each frame in the GIF with a progress bar
        for frame in tqdm(ImageSequence.Iterator(img), total=total_frames, desc="Processing frames"):
            frame = frame.convert("RGBA")
            datas = frame.getdata()

            new_data = []
            limit = 230
            for item in datas:
                # Change black (or nearly black) pixels to transparent
                if item[0] < limit and item[1] < limit and item[2] < limit:
                    # Change all black (also shades of black)
                    new_data.append((255, 255, 255, 0))
                else:
                    new_data.append(item)

            frame.putdata(new_data)
            frames.append(frame)

        # Save the frames as a new GIF
        frames[0].save(output_path, save_all=True, append_images=frames[1:], transparency=0, loop=0)
    
    elif ext in [".png", ".jpg", ".jpeg"]:
        img = img.convert("RGBA")
        datas = img.getdata()

        new_data = []
        limit = 250
        for item in datas:
            # Change black (or nearly black) pixels to transparent
            if item[0] > limit and item[1] > limit and item[2] > limit:
                # Change all black (also shades of black)
                new_data.append((255, 255, 255, 0))
            else:
                new_data.append(item)

        img.putdata(new_data)
        img.save(output_path)
    else:
        raise ValueError("Unsupported file format!")

# Example usage
# make_black_transparent("static/helper.gif", "static/helper_rb.gif")
make_black_transparent("static/SynopAI-Logo.jpg", "static/SynopAI-Logo-rb.png")