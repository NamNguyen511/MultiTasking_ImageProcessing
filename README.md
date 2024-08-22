# Image MutilTask Processing Application

Welcome to the Image Multitask Processing Application! This project is a Python-based image processing application using PyQt5 and OpenCV. It allows users to perform various image processing tasks such as color adjustments, morphological operations and more.

## Table of Contents

- [Features](#features)
- [Installation](#Installation)
- [Usage](#Usage)
- [Contributing](#Contributing)
- [Future Implementation](#future-implementation)
- [License](#Lisense)

## Features

- **Load and Save Images**: Easily load images from a computer and save the processes in various formats.
- **Color Adjustments**:
  - Adjust Hue and Saturation of an image
  - Balance the Red, Blue, and Green.
- **Morphological Operations**:
  - Apply different filters such as Rectangle, Ellipse, and Cross to perform operations such as Dilation, Erosion, Open, Closing, and Gradient, etc.
 
- **Image Rotation**: Rotate images at any angle with automatic cropping to remove black borders.
- **Image Histogram**: View the color histogram of the processed image.


## Installation

### Prerequisites

- Python 3.x
- [PyQt5](https://pypi.org/project/PyQt5/)
- [OpenCV](https://pypi.org/project/opencv-python/)
- [Matplotlib](https://pypi.org/project/matplotlib/)

### Clone the Repo

```bash
git clone https://github.com/yourusername/image_mutiltask-processing.git
cd image-multitask_processing
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

## Usage

### Running the application

To start the application, run the `main.py` file:

```bash
python main.py
```

### Using the application

1. **Loading an Image**: Use the "Load Image" button to load an image from your computer
2. **Saving an Image**: After processing, you can save the image using the "Save" option in the "File" menu.
3. **Color Adjustments**:
   - Adjust the Hue and Saturation using the sliders in the "Color Adjustments" section.
   - Modify the Red, Green, and Blue balance to enhance the image colors.
4. **Morphological Filters**:
   - Select the desired filter shape and type from the dropdown menus.
   - Click "Apply Filter" to show the result.
5. **Rotate Image**: Enter the angle of rotation and click "Rotate" to rotate an image.
6. **View Histogram**: Select "Show Histogram" from the "Image" menu to view the color distribution.


## Contributing
Contributions are welcome! Here's how you can help:
1. **Fork the repo**: Click the "Fork" button at the top-right corner of this page.
2. **Clone your fork**: Clone your forked repo to your local machine.
3. **Create a branch**: Create a new branch for your feature or bug fix.
   ```bash
    git checkout -b feature/your-feature-name
   ```
4. **Make changes**: Make your changes to the codebase.
5. **Commit your changes**: Commit your changes with a meaningful commit message.
   ```bash
    git commit -m "Add new feature: your feature name"
   ```
6. **Push you changes**: Push your changes to your forked repo
   ```bash
    git push origin feature/your-feature-name
   ```
7. **Create pull request**: Open a pull request to the main repo. Provide a clear description of the changes you made.

## Future implementations:
- Batch Processing: Allow users to apply operations to multiple images simutaneously.
- Advanced Filters: Implement filters like Gaussian Blur, Median Blur, and more.
- Machine Learning Integration: Add features like object detection, image classification, or style transfer using pre-trained models.
- Localization: Support multiple languages for a wider audience.
- Plugin System: Allow third-party developers to add new filters and features as plugins.

## License
This project is licensed under the MIT License.

  
