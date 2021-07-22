# Pull the base dash image for NAS, it has:
# -python 3.8, dash, dash-bootstrap-components, pyodbc, and waitress
#     installed in the dash_env enviroment
# -ODBC configuration with DNS for the Digitalization server called Digi
# -Nano and VIM for cmd line operations during troubleshooting
# -a folder called '/prj' for your project
FROM nas-dash-base

# Startup
WORKDIR "/prj"
COPY . .
ENTRYPOINT ["conda", "run", "-n", "dash_env"]
CMD ["python", "server.py"]