from toolsman.core import printc, now


class Printer:
    def output(self, content, color: str):
        printc(content, color)

    def red(self, content):
        self.output(content, 'red')

    def green(self, content):
        self.output(content, 'green')

    def yellow(self, content):
        self.output(content, 'yellow')

    def blue(self, content):
        self.output(content, 'blue')


printer = Printer()


class Loger(Printer):
    def output(self, content, color: str):
        message = f'{now()} - {content}'
        printc(message, color)


log = Loger()

if __name__ == '__main__':
    log.red("Hello")
    log.yellow("World")
    log.blue("Hello")
    log.green("World")
