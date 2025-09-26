### A demo of how to perform eye following with a live2d model and change model motion on click events using Renpy 8.4.1
Not profiled for performance, but the update_function parameter is executed in the render function of the Live2D class, which handles the general motion updates, so invoking it on a fixed 30 FPS seems reasonable.
![eyeFollow](https://github.com/user-attachments/assets/4aa28b86-24eb-4509-a14a-e434aeb95071)
