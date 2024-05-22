import cv2
import numpy as np
import argparse

def create_bouncing_ball_video(framerate=30, duration=10, file_name='bouncing_ball.mp4'):
    # Video settings
    width, height = 640, 480
    ball_radius = 20
    ball_color = (0, 255, 0)  # Green
    bg_color = (0, 0, 0)  # Black
    speed_x, speed_y = 5, 5

    # Initial position of the ball
    x, y = width // 2, height // 2

    # Total frames
    total_frames = int(framerate * duration)

    # Create a VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(file_name, fourcc, framerate, (width, height))

    for _ in range(total_frames):
        # Create a black image
        frame = np.zeros((height, width, 3), dtype=np.uint8)

        # Draw the ball
        cv2.circle(frame, (x, y), ball_radius, ball_color, -1)

        # Update the ball's position
        x += speed_x
        y += speed_y

        # Bounce off the walls
        if x - ball_radius <= 0 or x + ball_radius >= width:
            speed_x = -speed_x
        if y - ball_radius <= 0 or y + ball_radius >= height:
            speed_y = -speed_y

        # Write the frame to the video file
        out.write(frame)

    # Release the VideoWriter object
    out.release()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create a bouncing ball video.')
    parser.add_argument('--framerate', type=int, default=30, help='Frame rate of the video (default: 30)')
    parser.add_argument('--duration', type=int, default=10, help='Duration of the video in seconds (default: 10)')
    parser.add_argument('--filename', type=str, default='bouncing_ball.mp4', help='Output file name (default: bouncing_ball.mp4)')
    args = parser.parse_args()

    create_bouncing_ball_video(args.framerate, args.duration, args.filename)
