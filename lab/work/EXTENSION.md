# Bonus Extension E2 - Finding the Hang Boundary

## Prediction
Before running the experiment, I predicted that the naive MPI halo exchange would first hang at width 4096.

## Environment
Docker Compose with three containers: node0, node1 and node2.
Open MPI running six ranks from node0 as student.
Image height: 300 pixels.
Timeout: 10 seconds per test.

## Method
I generated images of different widths using make_test_image.py and ran img_mpi_v3_naive_halo.py with six MPI ranks.

Exit code 0 means the program completed.
Exit code 124 means the timeout killed the program.

## Measurements

| Width | Exit code |
|---|---|
| 256 | 0 |
| 1024 | 0 |
| 2048 | 0 |
| 2560 | 0 |
| 3072 | 0 |
| 3584 | 0 |
| 3712 | 0 |
| 3840 | 0 |
| 3968 | 0 |
| 4000 | 0 |
| 4032 | 0 |
| 4040 | 0 |
| 4041 | 124 |
| 4042 | 124 |
| 4043 | 124 |
| 4044 | 124 |
| 4045 | 124 |
| 4046 | 124 |
| 4047 | 124 |
| 4048 | 124 |
| 4056 | 124 |
| 4064 | 124 |
| 4096 | 124 |
| 8192 | 124 |

## Repeatability
Width 4040 completed successfully three times.
Width 4041 timed out three times.

## Command
for W in 4040 4041; do
  for R in 1 2 3; do
    timeout 10 mpirun --hostfile hostfile -n 6 python3 img_mpi_v3_naive_halo.py sw_$W sw_${W}_out > /dev/null 2>&1
    echo "width=$W run=$R exit=$?"
  done
done

## Conclusion
The narrowest observed boundary is between widths 4040 and 4041. The first width that timed out was 4041.

The result was surprising because my prediction was 4096, but the hang appeared earlier.

This is not a universal MPI constant. Another student may obtain a different boundary because MPI buffering, configuration, software versions and system resources can differ.

The underlying problem is the blocking Send-before-Recv communication pattern. Changing the message size only changes when the deadlock becomes visible.

## Evidence file
The repeated test results are saved in E2_evidence.txt.
