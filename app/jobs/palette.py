from PIL import Image
from matplotlib import image as image
from flask import current_app
import matplotlib.pyplot as plt
import skimage.io as io
import torch
import numpy as np
import skimage.color as convertor
import torchvision.transforms as transforms
from app.lib.palette_net.model import FeatureEncoder,RecoloringDecoder, get_dominant_colors
import os


def gen_style_img(catalog):

    FE = FeatureEncoder()
    RD = RecoloringDecoder()

    FE.load_state_dict(torch.load(os.path.join(current_app.config['MODEL_PATH'], "palette_net/FE.state_dict.pt")))
    RD.load_state_dict(torch.load(os.path.join(current_app.config['MODEL_PATH'], "palette_net/RD.state_dict.pt")))

    # large number test:

    # dir of content image 
    filename = os.listdir(os.path.join(catalog, "main/"))
    # dir of style image
    styleFilename = os.listdir(os.path.join(catalog, "style/"))

    for j,i in enumerate(filename):
        for styleFile in styleFilename: 
            
            img_np=io.imread(os.path.join(catalog, "main/") + filename[j])
            print(img_np.shape[-1])
            if img_np.shape[-1] != 3:
                img_np=img_np[:,:,:3]

            z = ((convertor.rgb2lab(img_np) - [50,0,0] ) / [50,127,127])

            img = torch.Tensor(z).permute(2,0,1)

            h = 32*int(img.shape[1]/32)
            w = 32*int(img.shape[2]/32)

            T = transforms.Resize((h,w))

            img = T(img)
            img = img.unsqueeze(0)
            illu = img[:,0:1,:,:]

            with torch.no_grad():
                c1,c2,c3,c4 = FE(img)

            palette = get_dominant_colors(os.path.join(catalog, "style/") + styleFile)[:6]
            
            print(palette)

            pal_np = np.array(palette).reshape(1,6,3)/255

            pal = torch.Tensor((convertor.rgb2lab(pal_np) - [50,0,0] ) / [50,128,128]).unsqueeze(0)


            print("here is your palette")
            plt.imshow(convertor.lab2rgb((pal[0].numpy() + [1,0,0]) * [50,128,128]));plt.axis(False)
            plt.show()

            palette = pal

            with torch.no_grad():
                out = RD(c1, c2, c3, c4, palette, illu)

                final_image = torch.cat([(illu+1)*50, out*128],axis = 1).permute(0,2,3,1)[0]
            _, ax= plt.subplots(1,3,squeeze=True,facecolor='w',dpi = 250, edgecolor='k')
            
            
#           ax[0].imshow(convertor.lab2rgb((pal[0].numpy() + [1,0,0]) * [50,128,128]));ax[0].axis(False);ax[0].set_title("Input palette")

            ax[0].imshow(image.imread(os.path.join(catalog, "style/") + styleFile));ax[0].axis(False);ax[0].set_title("Input palette")
            ax[1].imshow(convertor.lab2rgb((img[0].permute(1,2,0).numpy() + [1,0,0]) * [50,128,128]));ax[1].axis(False);ax[1].set_title("Input Image")
            ax[2].imshow(convertor.lab2rgb(final_image));ax[2].axis(False);ax[2].set_title("Output image")
            plt.show()

            plt.figure(num=None, figsize=(20, 6), dpi=80, facecolor='w', edgecolor='k')
            plt.imshow(convertor.lab2rgb(final_image));plt.axis(False)
            image.imsave(os.path.join(catalog, "output/") + filename[j].split('.')[0]+'_'+styleFile, convertor.lab2rgb(final_image))
            plt.show()

            # convertor.lab2rgb(final_image) can be saved as file 


    
