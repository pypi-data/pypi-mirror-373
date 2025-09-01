from textual.app import App


class S3Explorer(App):
    """A Textual app to explore s3 buckets"""

    BINDINGS = [("tab", "tab_bind", "change panel focus")]


if __name__ == "__main__":
    app = S3Explorer()
    app.run()
