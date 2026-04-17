import numpy as np
from PIL import Image as im
from scipy.ndimage import gaussian_filter, median_filter
import cv2


def denoise_image(input_path, output_path, strength=1.0, method='bilateral'):
    """
    ลด noise จากภาพ
    
    Parameters:
    -----------
    input_path : str
        ไฟล์ภาพที่ต้องการลด noise
    output_path : str
        ไฟล์ output
    strength : float
        ความแรงของ denoise (0.5-2.0)
        0.5 = อ่อน, 1.0 = กลาง, 2.0 = แรง
    method : str
        'bilateral' = ดีที่สุด (เก็บขอบ)
        'gaussian' = เร็ว (เบลอเล็กน้อย)
        'median' = กลาง
        'nlm' = ช้าแต่ดีมาก (Non-Local Means)
    
    Returns:
    --------
    str : output_path
    """
    
    print(f"🔧 Denoising: {input_path}")
    print(f"   Method: {method}")
    print(f"   Strength: {strength}")
    
    # โหลดภาพ
    img = im.open(input_path)
    img_array = np.array(img)
    
    if method == 'bilateral':
        # Bilateral Filter - ดีที่สุด (เก็บขอบคมชัด)
        d = int(9 * strength)  # diameter
        sigma_color = 75 * strength
        sigma_space = 75 * strength
        
        denoised = cv2.bilateralFilter(img_array, d, sigma_color, sigma_space)
        print(f"   ✓ Applied Bilateral Filter (d={d})")
        
    elif method == 'gaussian':
        # Gaussian Blur - เร็ว
        sigma = 1.0 * strength
        denoised = gaussian_filter(img_array, sigma=sigma)
        print(f"   ✓ Applied Gaussian Blur (sigma={sigma})")
        
    elif method == 'median':
        # Median Filter - ดีกับ salt-and-pepper noise
        size = int(3 * strength)
        if size % 2 == 0:
            size += 1
        denoised = median_filter(img_array, size=size)
        print(f"   ✓ Applied Median Filter (size={size})")
        
    elif method == 'nlm':
        # Non-Local Means - ช้าแต่ดีมาก
        h = 10 * strength
        denoised = cv2.fastNlMeansDenoisingColored(
            img_array,
            None,
            h=h,
            hColor=h,
            templateWindowSize=7,
            searchWindowSize=21
        )
        print(f"   ✓ Applied NLM Denoising (h={h})")
        
    else:
        print(f"   ✗ Unknown method: {method}")
        denoised = img_array
    
    # บันทึก
    output_img = im.fromarray(denoised.astype(np.uint8))
    output_img.save(output_path)
    
    print(f"   💾 Saved: {output_path}")
    print()
    
    return output_path


def compare_denoise_methods(input_path, output_prefix='denoised'):
    """
    เปรียบเทียบวิธี denoise ทั้งหมด
    
    Parameters:
    -----------
    input_path : str
        ไฟล์ภาพต้นฉบบ
    output_prefix : str
        prefix ของไฟล์ output
    """
    
    methods = ['bilateral', 'gaussian', 'median', 'nlm']
    
    print("=" * 70)
    print("  🔬 COMPARING DENOISE METHODS")
    print("=" * 70)
    print()
    
    for method in methods:
        output_path = f"{output_prefix}_{method}.png"
        denoise_image(input_path, output_path, strength=1.0, method=method)
    
    print("=" * 70)
    print("  ✅ DONE - Compare the results:")
    print("=" * 70)
    for method in methods:
        print(f"  • {output_prefix}_{method}.png")
    print("=" * 70)


def denoise_progressive(input_path, output_prefix='denoised', strengths=[0.5, 1.0, 1.5, 2.0]):
    """
    ทดสอบความแรงต่างๆ
    
    Parameters:
    -----------
    input_path : str
        ไฟล์ภาพต้นฉบบ
    output_prefix : str
        prefix ของไฟล์ output
    strengths : list
        ความแรงที่ต้องการทดสอบ
    """
    
    print("=" * 70)
    print("  📊 TESTING DIFFERENT STRENGTHS")
    print("=" * 70)
    print()
    
    for strength in strengths:
        output_path = f"{output_prefix}_strength_{strength:.1f}.png"
        denoise_image(input_path, output_path, strength=strength, method='bilateral')
    
    print("=" * 70)
    print("  ✅ DONE - Compare the results:")
    print("=" * 70)
    for strength in strengths:
        print(f"  • {output_prefix}_strength_{strength:.1f}.png")
    print("=" * 70)

