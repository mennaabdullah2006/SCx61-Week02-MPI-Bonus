\# AI Usage Log



\## SCx61 Week 2 - MPI Point-to-Point Communication



\## 1. Purpose



I used ChatGPT as a learning and debugging assistant while completing the MPI image filtering lab and bonus extension E2.



AI helped me understand MPI concepts, organize experiments, interpret terminal outputs and prepare documentation.



The experimental measurements were obtained from commands executed in my Docker environment.



\## 2. How I Used AI



| Task | AI Assistance | My Verification |

|---|---|---|

| Understanding halo exchange | Explained why a 3x3 filter needs neighbouring rows | Compared v1 and v2 against the serial reference |

| MPI deadlock investigation | Explained blocking sends, receives and MPI buffering | Reproduced the timeout in the Docker cluster |

| Synchronous communication | Suggested testing MPI.Ssend | Observed a timeout at width 256 |

| Eager limit investigation | Explained how buffering can affect MPI.Send | Tested widths 8192 and 20000 |

| Bonus E2 | Helped organize a width-sweep experiment | Repeated tests at widths 4040 and 4041 |

| Documentation | Helped structure the README and incident report | Checked GitHub rendering and compared the reports with recorded results |

| GitHub publication | Explained Git commands and file selection | Checked staged files and confirmed the successful push |



\## 3. Example AI-Assisted Investigation



\### Question



Why does the naive MPI halo exchange complete for some image widths but hang for larger ones?



\### AI Explanation



MPI.Send may complete using internal buffering for some messages. For larger messages, it may need the matching receive to be posted before it completes.



If neighbouring ranks both send first and receive later, the program may deadlock.



\### Verification



I tested the naive implementation with different image widths and a 10-second timeout.



The program completed at width 4040 and timed out at width 4041.



I repeated both tests three times and observed the same results.



This supported the explanation that the failure depended on message size and MPI communication behavior.



\## 4. An AI Suggestion That Was Not a Complete Fix



One investigated approach was increasing the MPI eager limit.



With an eager limit of 16384, the naive implementation completed at width 8192.



However, it timed out at width 20000.



Therefore, changing the eager limit was not a reliable solution to the underlying communication-ordering problem.



The corrected implementation used MPI.Sendrecv.



\## 5. Independent Checks



I checked the experimental results using:



\- Terminal output and process exit codes.

\- A serial image filtering reference.

\- NumPy array equality checks.

\- Differing-pixel counts.

\- Repeated runs at the observed hang boundary.

\- GitHub file and README rendering checks.



\## 6. Limitations



AI explanations and suggestions were not treated as experimental evidence.



The observed hang boundary is specific to the tested environment.



The public repository does not include the restricted course Break Kit files.



\## 7. Reflection



AI was useful for understanding MPI concepts and planning systematic debugging experiments.



The most important lesson was to test suggestions rather than assume they were correct.



The eager-limit experiment demonstrated why a program completing once does not necessarily mean the underlying communication problem has been fixed.



\## 8. AI Tool Disclosure



Tool used: OpenAI ChatGPT.



Main uses: concept explanations, debugging guidance, experiment planning, documentation drafting and GitHub workflow assistance.



All reported numerical results were checked against the outputs of the lab experiments.
