from .radioplayer import RadioPlayerApp

app = RadioPlayerApp()
app.command()(radioplayer)

if __name__ == "__main__":
    app.run()