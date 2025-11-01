# Creating a Slit-Scan Effect Using TouchDesigner Texture Operators

## Basic Slit-Scan Effect
Created a slit-scan effect in TouchDesigner by first making a video input into a 3D texture. I then created the input for the effect with a ramp node into a limit node. I also used a displacement node with noise as the first input and the limit node as the second input, which was added as the second input to a time machine node. The time machine node ouput was the input for the final out node. The video below shows a demo of the output, and the link below that is to the tutorial I used, made by Clara Nolan, a TA for Procedural Computer Graphics at Penn.

[SlitScanMovie](slitScanDemo.mp4)

Link to tutorial: https://youtu.be/fz_PxG5KoNE

## Exploration of Effects
I explored some of the other texture operators in TouchDesigner and added a lens distortion node which I used to create a fisheye lens effect. I used the fisheye lens output as input for a threshold node which uses a threshold to make all pixels empty or white depending on if they are above or below the threshold. I used the default threshold property of luminance, slightly lowered the threshold to 0.42, made the alpha one instead of RGB to fill in the blank pixels with black, and increased the soften property just a bit. I really like the output becuase it reminds me of something you would see in a music video. The video is linked below.

[FisheyeBWMovie](fisheyeThreshold.mp4)
