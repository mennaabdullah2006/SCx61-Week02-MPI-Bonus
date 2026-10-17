\# MPI Deadlock Incident Report



\## 1. Incident Summary



During SCx61 Week 2, I investigated a deadlock in a naive MPI halo exchange implementation.



The program divided a grayscale image into horizontal strips across six MPI ranks running in three Docker containers.



The naive implementation attempted blocking sends before posting the matching receives. This communication pattern could cause the processes to wait indefinitely.



I reproduced the problem, investigated its relationship with message size and MPI buffering, and verified that using `MPI.Sendrecv` resolved the communication problem.



\## 2. Environment



\- Operating system: Windows

\- Development tools: VS Code and Docker Desktop

\- Cluster: Three Docker containers (node0, node1, node2)

\- MPI processes: Six ranks

\- MPI implementation: Open MPI

\- Programming language: Python

\- Libraries: mpi4py and NumPy



The experiments were performed inside the Docker-based course lab environment.



\## 3. Expected Behavior



Each MPI rank should exchange the necessary halo rows with its neighbouring ranks.



After receiving the halo rows, each rank should apply the 3x3 box blur to its image strip.



The program should then collect the processed strips and produce an output identical to the serial reference.



\## 4. Observed Failure



I tested the naive halo exchange program with an image width of 8192 pixels.



The six ranks printed:



```text

before Send

```



However, the expected messages after the blocking send did not appear.



The program failed to complete within the timeout.



This indicated that the ranks were blocked during communication.



\## 5. Root Cause Analysis



The naive implementation used blocking MPI sends before the corresponding receives were posted.



A simplified example of the problematic communication pattern is:



```python

comm.Send(send\_buffer, dest=neighbor)

comm.Recv(recv\_buffer, source=neighbor)

```



If neighbouring ranks both attempt blocking sends before posting receives, progress may depend on whether MPI can buffer the outgoing messages.



For smaller messages, `MPI.Send` may complete using internal buffering.



For larger messages, it may wait until a matching receive is posted.



If both neighbours are waiting inside their sends, neither reaches the receive operation.



This creates a communication deadlock.



The exact message size at which this behavior appears depends on the MPI implementation, transport and configuration.



\## 6. Experiments and Evidence



\### Experiment A: Large message



I ran the naive implementation with image width 8192.



\*\*Observation:\*\* All six ranks reached `before Send`, but the program timed out before completing the communication.



\*\*Conclusion:\*\* The communication pattern could hang for large messages.



\### Experiment B: Synchronous send



I tested `MPI.Ssend` with image width 256.



\*\*Observation:\*\* The program timed out with exit code 124.



\*\*Conclusion:\*\* Synchronous sends exposed the unsafe send-before-receive ordering even for a smaller message.



\### Experiment C: Increasing the eager limit



I tested the MPI configuration option:



```text

\--mca btl\_vader\_eager\_limit 16384

```



With this setting, the naive implementation completed at width 8192.



However, the same approach hung at width 20000.



\*\*Conclusion:\*\* Increasing the eager limit changed when the problem appeared, but did not fix the underlying communication ordering.



\### Experiment D: Corrected halo exchange



I tested the corrected implementation using `MPI.Sendrecv`.



The corrected version completed successfully at width 8192.



The output matched the serial reference:



```text

np.array\_equal: True

Differing pixels: 0 / 2457600

```



I repeated the verification three times and obtained the same result.



\*\*Conclusion:\*\* The corrected implementation completed successfully and preserved numerical correctness in the tested configuration.



\## 7. Resolution



The correct solution was to replace the unsafe send-before-receive sequence with coordinated communication using `MPI.Sendrecv`.



A simplified example is:



```python

comm.Sendrecv(

&#x20;   sendbuf=send\_buffer,

&#x20;   dest=neighbor,

&#x20;   recvbuf=recv\_buffer,

&#x20;   source=neighbor

)

```



`MPI.Sendrecv` combines a send and receive operation so that neighbouring ranks can exchange data without requiring both to complete a blocking send first.



This avoids the deadlock pattern observed in the naive implementation when matching communication operations are correctly arranged.



\## 8. Bonus E2: Finding the Hang Boundary



I also investigated the image width where the naive implementation began hanging on my setup.



I used a 10-second timeout for each run.



My repeated measurements showed:



| Image width | Run 1 | Run 2 | Run 3 |

|---:|---:|---:|---:|

| 4040 | Completed | Completed | Completed |

| 4041 | Timed out | Timed out | Timed out |



The observed boundary was between widths \*\*4040 and 4041\*\*.



This is a machine-specific observation, not a universal MPI threshold.



Detailed evidence is available in:



\- \[Extension report](lab/work/EXTENSION.md)

\- \[E2 experiment evidence](lab/work/E2\_evidence.txt)



\## 9. Lessons Learned



1\. Blocking `MPI.Send` does not guarantee that a matching receive has already occurred.

2\. MPI buffering can allow unsafe communication patterns to appear correct for smaller messages.

3\. Changing the eager limit may change the observed behavior without correcting the program.

4\. `MPI.Ssend` is useful for exposing communication-ordering problems.

5\. `MPI.Sendrecv` provides a safer approach for coordinated halo exchanges.

6\. Correctness should be verified against an independent serial implementation.

7\. Repeating experiments helps distinguish consistent observations from one-time behavior.



\## 10. Final Outcome



The incident was successfully reproduced and investigated.



The naive implementation demonstrated a communication hang under specific message sizes.



The corrected `MPI.Sendrecv` implementation completed the tests and produced output identical to the serial reference.



The investigation improved my understanding of blocking MPI communication, buffering and deadlock prevention.



\## Course Credit



SCx61 Distributed Computing, Week 2.



Course materials provided by Norhan Saber, Teaching Assistant, Scientific Computing Department, Faculty of Computers and Artificial Intelligence, Benha University.
