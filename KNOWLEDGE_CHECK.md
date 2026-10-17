\# Knowledge Check



\## SCx61 Week 2 - MPI Point-to-Point Communication



\### 1. What is MPI?



MPI stands for Message Passing Interface. It allows processes to communicate by sending and receiving messages.



In this lab, I used six MPI ranks distributed across three Docker containers.



\### 2. What is a rank?



A rank is the unique identifier of a process within an MPI communicator.



For example, rank 0 was responsible for distributing image strips and collecting the final results.



\### 3. Why did we divide the image into strips?



Dividing the image allowed different MPI processes to work on different parts of the image.



Each rank processed a horizontal strip using a 3x3 box blur.



\### 4. What is halo exchange?



Halo exchange is the process of sharing boundary data between neighbouring MPI ranks.



A 3x3 filter needs pixels from the rows immediately above and below the current row.



Without halo exchange, ranks cannot correctly process pixels near the boundaries of their assigned strips.



\### 5. What was wrong with version 1?



Version 1 did not exchange halo rows.



As a result, it produced incorrect pixels at strip boundaries.



My experiment found 4188 differing pixels compared with the serial reference.



\### 6. How did version 2 solve the problem?



Version 2 used MPI.Sendrecv to exchange halo rows between neighbouring ranks.



After the exchange, each rank had the neighbouring data needed to apply the filter correctly.



The output matched the serial reference with zero differing pixels.



\### 7. What is the difference between MPI.Send and MPI.Ssend?



MPI.Send is a standard blocking send. Depending on the MPI implementation and message size, it may complete using internal buffering.



MPI.Ssend is a synchronous blocking send. It completes only after the matching receive has been initiated.



Both require correctly matched communication operations.



\### 8. What causes an MPI deadlock?



A deadlock occurs when processes are waiting for communication operations that cannot make progress.



In the naive implementation, neighbouring ranks attempted blocking sends before posting their matching receives.



For sufficiently large messages, both ranks could become blocked.



\### 9. Why did the naive implementation sometimes work?



MPI may buffer smaller messages, allowing MPI.Send to complete before a matching receive is posted.



For larger messages, the send may wait for the receiver.



This explains why the unsafe communication pattern could appear to work for some image widths but hang for others.



\### 10. Why is increasing the eager limit not a proper fix?



Increasing the eager limit can change which messages are buffered.



In my experiment, the naive implementation completed at width 8192 with a higher eager limit but timed out at width 20000.



The unsafe communication order remained unchanged.



\### 11. How does MPI.Sendrecv help?



MPI.Sendrecv combines a send and receive operation.



When neighbouring processes use correctly matched Sendrecv calls, they can exchange data without both becoming stuck in a send-first sequence.



This was the approach used in the corrected implementation.



\### 12. What does exit code 124 mean?



In my experiments, exit code 124 indicated that the Linux timeout command stopped the process because it exceeded the 10-second limit.



It was evidence that the program did not complete within the allowed time.



\### 13. What did I discover in bonus extension E2?



I tested different image widths to identify where the naive implementation began hanging.



The observed boundary was between widths 4040 and 4041.



Width 4040 completed successfully in three repeated runs.



Width 4041 timed out in three repeated runs.



\### 14. Is 4041 a universal MPI deadlock threshold?



No.



The threshold depends on factors such as the MPI implementation, communication configuration, message size and runtime environment.



Another machine may produce a different result.



\### 15. How did I verify correctness?



I compared the MPI output against a serial reference.



I used NumPy array equality checks and differing-pixel counts.



For the corrected version, the 8192-wide image produced zero differing pixels across three repeated runs.



\## Final Reflection



This lab helped me understand how MPI processes communicate, why neighbouring data is important in parallel image filtering, and how unsafe blocking communication can cause deadlocks.



I also learned that experimental evidence is essential when investigating parallel programs because a solution that works for one message size may fail for another.
