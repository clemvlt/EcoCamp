from application.application import Application

monApp = Application()
application = monApp.app

if __name__ == "__main__":
    application.run(host='0.0.0.0', port=8000, debug=True)
