import os
import imageio
from tqdm import tqdm
from pygifsicle import optimize


def convert(dir, title):
    path = f'{title}.gif'
    with imageio.get_writer(path, mode='I') as writer:
        for filename in tqdm(os.listdir(dir)):
            image = imageio.imread(dir+filename)
            writer.append_data(image)
    print("GIF Generated! Optimizing...")
    optimize(path)
    print("Optimized!")


convert("out/img-202004/", "202004")
