# 2023_study

The LLM inference stuff is in `perf scripts/fast.py`. 

The rest of the stuff is mainly LLMOps type stuff like:

Right now we have the fast.py file running behind nginx using systemd as the process manager. 
The script files for all this are inside the 

The see the logs use: 
`sudo journalctl --unit=systemd_llm`

To follow logs in real time:

`sudo journalctl -f -u systemd_llm`