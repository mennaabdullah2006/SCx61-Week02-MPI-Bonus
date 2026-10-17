#!/usr/bin/env python3
"""
SCx61 Week 2 — Lab Step 5: row-strip decomposition,
NO halo exchange.

Rank 0 splits the image into row strips and sends each
worker its strip. Each rank filters its own strip, then
rank 0 gathers the results.

This version intentionally has no halo exchange.
"""

import socket
import numpy as np
from mpi4py import MPI

IN_PREFIX = "test_image"
OUT_PREFIX = "test_image_filtered_v1"


def box_blur_3x3(img: np.ndarray) -> np.ndarray:
    """Apply a 3x3 box blur with edge replication."""
    padded = np.pad(img.astype(np.float64), pad_width=1, mode="edge")
    acc = np.zeros_like(img, dtype=np.float64)
    h, w = img.shape

    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            acc += padded[1 + dy: 1 + dy + h,
                          1 + dx: 1 + dx + w]

    acc /= 9.0
    return np.clip(acc, 0, 255).astype(np.uint8)


def split_rows(height: int, n: int):
    """Split image rows as evenly as possible."""
    base = height // n
    extra = height % n
    bounds = []
    start = 0

    for i in range(n):
        rows = base + (1 if i < extra else 0)
        bounds.append((start, start + rows))
        start += rows

    return bounds


def main():
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()
    hostname = socket.gethostname()

    if rank == 0:
        img = np.load(f"{IN_PREFIX}.npy")
        height, width = img.shape
        bounds = split_rows(height, size)

        print(
            f"[rank 0 on {hostname}] image {img.shape}, "
            f"split into {size} strips: {bounds}",
            flush=True
        )

        my_start, my_end = bounds[0]
        my_strip = img[my_start:my_end, :].copy()

        # Send each worker its image strip
        for worker in range(1, size):
            w_start, w_end = bounds[worker]
            worker_strip = img[w_start:w_end, :].copy()

            comm.send(worker_strip.shape, dest=worker, tag=10)
            comm.Send(worker_strip, dest=worker, tag=11)

        my_filtered = box_blur_3x3(my_strip)

        # Gather filtered strips
        result = np.zeros_like(img)
        result[my_start:my_end, :] = my_filtered

        for worker in range(1, size):
            w_start, w_end = bounds[worker]

            shape = comm.recv(source=worker, tag=20)
            buf = np.empty(shape, dtype=np.uint8)
            comm.Recv(buf, source=worker, tag=21)

            result[w_start:w_end, :] = buf

        np.save(f"{OUT_PREFIX}.npy", result)

        print(
            f"[rank 0 on {hostname}] wrote {OUT_PREFIX}.npy "
            f"(NO halo — expect seams at strip boundaries)",
            flush=True
        )

    else:
        # Receive image strip from rank 0
        shape = comm.recv(source=0, tag=10)
        strip = np.empty(shape, dtype=np.uint8)
        comm.Recv(strip, source=0, tag=11)

        print(
            f"[rank {rank} on {hostname}] received strip "
            f"{shape}, filtering alone (no halo)",
            flush=True
        )

        filtered = box_blur_3x3(strip)

        # Send filtered result to rank 0
        comm.send(filtered.shape, dest=0, tag=20)
        comm.Send(filtered, dest=0, tag=21)


if __name__ == "__main__":
    main()