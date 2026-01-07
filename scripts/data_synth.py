import cv2
import numpy as np
import os
import random
from pathlib import Path

class DataSynthesizer:
    def __init__(self, icons_config, background_dir, output_dir='dataset'):
        """
        icons_config: list of dicts [{'path': str, 'class': int}]
        """
        self.icons = []
        for icon_cfg in icons_config:
            icon = cv2.imread(icon_cfg['path'], cv2.IMREAD_UNCHANGED if icon_cfg['path'].endswith('.png') else cv2.IMREAD_COLOR)
            if icon is not None:
                self.icons.append({'img': icon, 'class': icon_cfg['class']})
        
        if not self.icons:
            raise ValueError("Could not load any icons.")
            
        self.bg_paths = list(Path(background_dir).glob('*.png')) + list(Path(background_dir).glob('*.jpg'))
        self.output_dir = Path(output_dir)
        (self.output_dir / 'images' / 'train').mkdir(parents=True, exist_ok=True)
        (self.output_dir / 'labels' / 'train').mkdir(parents=True, exist_ok=True)

    def overlay_transparent(self, background, overlay, x, y):
        background_width, background_height = background.shape[1], background.shape[0]
        if x >= background_width or y >= background_height:
            return background

        h, w = overlay.shape[0], overlay.shape[1]
        if x + w > background_width:
            w = background_width - x
            overlay = overlay[:, :w]
        if y + h > background_height:
            h = background_height - y
            overlay = overlay[0:h, :]

        if overlay.shape[2] < 4:
            background[y:y+h, x:x+w] = overlay
            return background

        overlay_image = overlay[..., :3]
        mask = overlay[..., 3:] / 255.0

        background[y:y+h, x:x+w] = (1.0 - mask) * background[y:y+h, x:x+w] + mask * overlay_image
        return background

    def generate(self, count=500):
        for i in range(count):
            bg_path = random.choice(self.bg_paths)
            bg = cv2.imread(str(bg_path))
            if bg is None: continue

            # Randomly pick 1 or 2 icons to place
            num_to_place = random.randint(1, 2)
            img = bg.copy()
            labels = []
            
            bh, bw = bg.shape[:2]

            for _ in range(num_to_place):
                icon_data = random.choice(self.icons)
                icon_img = icon_data['img']
                cls_id = icon_data['class']

                # Random scale
                scale = random.uniform(0.5, 1.2)
                icon_resized = cv2.resize(icon_img, None, fx=scale, fy=scale)
                
                h, w = icon_resized.shape[:2]
                
                if bh < h or bw < w: continue
                
                x = random.randint(0, bw - w)
                y = random.randint(0, bh - h)
                
                # Apply icon
                if icon_resized.shape[2] == 4:
                    img = self.overlay_transparent(img, icon_resized, x, y)
                else:
                    img[y:y+h, x:x+w] = icon_resized[..., :3]

                # Save label info
                x_center = (x + w / 2) / bw
                y_center = (y + h / 2) / bh
                width = w / bw
                height = h / bh
                labels.append(f"{cls_id} {x_center} {y_center} {width} {height}")

            # Save image
            img_name = f"synth_{i:04d}.jpg"
            cv2.imwrite(str(self.output_dir / 'images' / 'train' / img_name), img)

            # Save labels
            with open(self.output_dir / 'labels' / 'train' / f"synth_{i:04d}.txt", 'w') as f:
                f.write("\n".join(labels) + "\n")

        print(f"Generated {count} images in {self.output_dir}")

if __name__ == "__main__":
    icons_config = [
        {'path': 'data/retry_icon.png', 'class': 0},
        {'path': 'data/continue_btn.png', 'class': 0},  # Both are "retry" actions
        {'path': 'data/error_msg.png', 'class': 1}      # Error status
    ]
    background_dir = 'data/backgrounds'
    output_dir = 'dataset'
    
    ds = DataSynthesizer(icons_config, background_dir, output_dir)
    ds.generate(600)
