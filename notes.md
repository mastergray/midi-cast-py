## Setting Up venv (With A Specific Version Of Python)

I had to do this since I had upgraded to Python 3.11 for another project - system wide - which then broke ubuntu because it needs to use Python 3.8.

To manage different versions of Python, you can use something like:

> sudo update-alternatives --config python3

And select which Python you want the system to use. **HOWVER**, _I_ only had 3.11 to choose from, so I needed to "register" 3.8 to us. So, I had to go find what versions of Python I had using the command:

> ls /usr/bin/python*

Which returned something like:

```bash
/usr/bin/python2    /usr/bin/python3     /usr/bin/python3.8         /usr/bin/python3-config    /usr/bin/python3-pasteurize
/usr/bin/python2.7  /usr/bin/python3.11  /usr/bin/python3.8-config  /usr/bin/python3-futurize
```

Then, to register the version I needed - the internet told me to run:

> sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.8 1

Which I guess means:

- `/usr/bin/python3` is the symlink managed by `update-alternatives`.
- `python3 is the name` of the alternative group.
- `/usr/bin/python3.8` is the path to the Python 3.8 executable.
- `1` is the priority (higher numbers have higher priority).

Running this command _again_ now let me choose 3.8:

> sudo update-alternatives --config python3

And I could verify with the following command:

> python3 --version

Which confirmed I was back to 3.8:

```bash
Python 3.8.10
```

So after I fixed terminal, I still needed to use a different version of Python than the system default. To do so, I could a leverage a [virtual enviroment](https://docs.python.org/3/library/venv.html) using the following command:

> /usr/bin/python3.11 -m venv my-virtual-env

Where my path to the version of Python I wanted to create the virtal enviroment for was found with `ls /usr/bin/python*` (the same command I found the 3.8 version I needed to use for the system default)

To "activate" the venv **my-virtual-env**, you use the command:

> source my-virtual-env/bin/activate

Which then show something like for your terminal:

> (my-virtual-env) $ 

Then you can install dependencies specific to that enviroment. If you want to save those dependences, you can run 

> pip3 freeze > requirements.txt

And then to install those dependences (to another enviroment), you would run

> pip3 install -r requirements.txt

To "decativate" the venv, you use 

> deactivate



### Note

- You **can't change the version of Python** a venv is running - so you'd need to recreate that venv by saving dependencies using `pip3 freeze > requirements.txt` and remove that venv using the command `rm -rf my-virtual-env`.
Then, you'd create a _new_ venv and reinstall those dependencies using `pip3 install -r requirements.txt`
