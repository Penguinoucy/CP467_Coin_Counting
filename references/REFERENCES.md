# References and links
Access date for web documentation: November 22, 2026. Documentation covers the APIs used;
the actual measurement environment used OpenCV 5.1.0 and is recorded in docs/hardware.json.

1. OpenCV contributors. *Hough Circle Transform*. OpenCV documentation.
   https://docs.opencv.org/4.x/d4/d70/tutorial_hough_circle.html
   Used for the gradient Hough baseline and radius/threshold controls.
2. Otsu, N. (1979). A Threshold Selection Method from Gray-Level Histograms.
   *IEEE Transactions on Systems, Man, and Cybernetics*, 9(1), 62-66.
   https://doi.org/10.1109/TSMC.1979.4310076
3. OpenCV contributors. *Image Thresholding*. OpenCV-Python documentation.
   https://docs.opencv.org/4.x/d7/d4d/tutorial_py_thresholding.html
   Used for the global Otsu implementation.
4. Suzuki, S., and Abe, K. (1985). Topological structural analysis of digitized binary images by border following.
   *Computer Vision, Graphics, and Image Processing*, 30(1), 32-46.
   https://doi.org/10.1016/0734-189X(85)90016-7
5. OpenCV contributors. *Finding contours in your image*. OpenCV documentation.
   https://docs.opencv.org/4.x/df/d0d/tutorial_find_contours.html
   Used for external contour extraction; area, perimeter, and moments filter candidates.
6. OpenCV contributors. *Morphological Transformations*. OpenCV-Python documentation.
   https://docs.opencv.org/4.x/d9/d61/tutorial_py_morphological_ops.html
   Used for opening and closing with elliptical kernels.
7. OpenCV contributors. *Histograms - 2: Histogram Equalization*. OpenCV-Python documentation.
   https://docs.opencv.org/4.x/d5/daf/tutorial_py_histogram_equalization.html
   Used for CLAHE before method-specific smoothing.
8. SciPy contributors. *scipy.optimize.linear_sum_assignment*. SciPy reference documentation.
   https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.linear_sum_assignment.html
   Used with explicit dummy costs to maximize valid matches, then minimize centre distance.
9. Dutta, A., and Zisserman, A. (2019). The VIA Annotation Software for Images, Audio and Video.
   *Proceedings of the 27th ACM International Conference on Multimedia*, 2276-2279.
   https://doi.org/10.1145/3343031.3350535
   Tool: https://www.robots.ox.ac.uk/~vgg/software/via/
   Source of the supplied manually drawn circle annotations.

# Project repository
https://github.com/Penguinoucy/CP467_Coin_Counting
The supplied project is a local snapshot. This delivery does not push changes to GitHub.
For a private course submission, the group must verify instructor and TA access.
