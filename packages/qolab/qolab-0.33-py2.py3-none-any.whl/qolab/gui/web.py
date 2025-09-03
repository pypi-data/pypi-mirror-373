import justpy as jp
import asyncio
import matplotlib.pyplot as plt

import logging

logger = logging.getLogger("qolab.gui.web")

button_classes = (
    "bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-full"
)
label_div_classes = "py-1 px-2"
checkbox_classed = label_div_classes
labelnames_classes = "font-bold"
panel_div_classes = "space-x-4 border"
controls_div_classes = "flex flex-wrap space-x-4 p-1 border"
controls_group_classes = "flex flex-wrap space-x-4 p-1"
dict_classes = "px-2 border-2"
dict_components_classes = "flex flex-wrap border-2"
input_classes = (
    "m-2 bg-gray-200"
    + " border-2 border-gray-200"  # noqa: W503 disables flake8 warning
    + " rounded w-20 text-gray-700"  # noqa: W503
    + " focus:outline-none focus:bg-white focus:border-purple-500"  # noqa: W503
)


class QOLPushButton(jp.Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_classes(
            "bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-full"
        )


class QOLPushButtonNoUndo(QOLPushButton):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_classes(
            "bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded-full"
        )


class QOLParamHeader(jp.Div):
    def __init__(self, label="NameNotSet", value=None, **kwargs):
        super().__init__(**kwargs)
        root = self
        root.label = label
        root.set_classes(label_div_classes)
        root.data[label] = None
        jp.Span(text=f"{label}: ", classes=labelnames_classes, a=root)
        self.setValue(value)

    def getValue(self):
        return self.data[self.label]

    def setValue(self, val):
        # print(f'setting {self.label} to {val}')
        self.data[self.label] = val


class QOLParamReadOnly(QOLParamHeader):
    """Read Only from the web point of view"""

    def __init__(self, label="NameNotSet", **kwargs):
        super().__init__(label=label, **kwargs)
        root = self
        jp.Span(model=[root, label], a=root)


class QOLParamReadWrite(QOLParamHeader):
    def __init__(self, label="NameNotSet", **kwargs):
        super().__init__(label=label, **kwargs)
        root = self
        self.input = jp.InputChangeOnly(
            classes=input_classes, model=[root, label], a=root, spellcheck="false"
        )


class QOLCheckbox(jp.Label):
    def __init__(self, label="NameNotSet", **kwargs):
        super().__init__(**kwargs)
        root = self
        root.data["checked"] = False
        root.label = label
        root.set_classes(checkbox_classed)
        jp.Input(
            type="checkbox", model=[root, "checked"], classes="form-checkbox", a=root
        )
        jp.Span(text=label, a=root)

    def getValue(self):
        return self.data["checked"]

    def setValue(self, val):
        self.data["checked"] = val


class QOLTimeLog(jp.Div):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = self
        root.traces = None
        # log must have 'plot' and 'clear_data' methods
        root.set_classes(panel_div_classes)
        dcontrols = jp.Div(a=root)
        dcontrols.set_classes(controls_div_classes)
        QOLPushButtonNoUndo(a=dcontrols, text="Clear log", click=self._clear_data)
        QOLPushButton(a=dcontrols, text="Replot", click=self._replot)
        self.update_interval = QOLParamReadOnly(
            label="UpdateInterval", value=5, a=dcontrols
        )
        self.save_controls = QOLSaveControls(
            component_with_data=self.traces, a=dcontrols
        )

        self.chart = jp.Matplotlib(a=root)
        self.start_task()

    def setTraces(self, component_with_data=None):
        self.traces = component_with_data
        self.save_controls.component_with_data = component_with_data

    def start_task(self):
        jp.run_task(self.update_loop())

    def stop_tasks(self):
        self.save_controls.stop_tasks()
        pass

    async def _clear_data(self, msg):
        self.clear_data()
        await self.update()

    def clear_data(self):
        traces = self.traces
        if traces is not None:
            traces.clear_data()
            self.plot()

    async def _replot(self, msg):
        self.plot()
        await self.update()

    async def update_loop(self, update_interval=None):
        if update_interval is not None:
            self.update_interval.setValue(update_interval)
        while True:
            self.plot()
            try:
                strwtime = self.update_interval.getValue()
                wtime = float(strwtime)
            except ValueError:
                wtime = 2
                print(f"Warning cannot convert {strwtime} setting to {wtime}")
            await self.update()
            await asyncio.sleep(wtime)

    def plot(self):
        traces = self.traces
        f = plt.figure(figsize=(8, 6), tight_layout=True)
        if traces is None:
            plt.title("Log data is unavailable")
        else:
            traces.plot()
        self.chart.set_figure(f)
        plt.close(f)


class QOLSaveControls(jp.Div):
    def __init__(self, component_with_data=None, **kwargs):
        super().__init__(**kwargs)
        root = self
        root.set_classes(controls_group_classes)

        root.component_with_data = component_with_data
        root.getNextDataFile = None
        root.bsave = QOLPushButton(a=root, text="Save", name="Save", click=self._save)
        root.bnext_file = QOLPushButton(
            a=root, text="Next file", name="NextFile", click=self._next_file
        )
        self.autosave_flag = QOLCheckbox(label="autosave", a=root)
        self.autosave_interval = QOLParamReadOnly(
            label="AutoSaveInterval", value=10, a=root
        )
        self.file_name = QOLParamReadOnly(label="FileName", a=root)
        self.start_task()

    def start_task(self):
        jp.run_task(self.autosave_loop())

    def stop_tasks(self):
        pass

    async def autosave_loop(self):
        while True:
            if self.autosave_flag.getValue():
                self.save()
            await asyncio.sleep(10)

    async def _save(self, msg):
        self.save()

    def save(self):
        fname = self.file_name.getValue()
        if fname is None:
            return
        if self.component_with_data is None:
            return
        logger.debug(f"saving to {fname}")
        self.component_with_data.save(fname)

    async def _next_file(self, msg):
        self.next_file()
        await self.update()

    def next_file(self):
        if self.getNextDataFile is not None:
            fname = self.getNextDataFile()
            logger.info(f"Data will be saved to {fname}")
            self.file_name.setValue(fname)
            if self.component_with_data is not None:
                self.component_with_data.clear_last_saved_pos()


class QOLDictionary(jp.Div):
    def __init__(self, container=None, **kwargs):
        super().__init__(**kwargs)
        root = self
        root.set_classes(dict_classes)
        self.dlabel = jp.Div(a=root, classes="bg-gray-100")
        self.dlabel.on("click", self._toggle_show)
        root.slabel = jp.Span(text=self.name, a=root.dlabel)
        root.slabel.set_classes(labelnames_classes)
        self.c = jp.Div(a=root)
        root.c.set_classes(dict_components_classes)
        root.container = container
        self.display_container_dictionary()

    async def _toggle_show(self, msg):
        self.c.show = not self.c.show

    def display_container_dictionary(self):
        self.c.delete_components()
        if self.container is None:
            return
        for k, v in self.container.items():
            if not isinstance(v, dict):
                QOLParamReadOnly(label=k, value=v, a=self.c)
            else:
                QOLDictionary(container=v, name=k, a=self.c)


def gui_test():
    return wp


if __name__ == "__main__":
    wp = jp.WebPage(delete_flag=False)
    rw = QOLParamReadWrite(label="ReadWriteParam", a=wp)
    rw.setValue(12345)

    log = QOLTimeLog(a=wp)
    log.save_controls.getNextDataFile = lambda: "data.dat"

    def test(self, msg):
        print(rw.getValue())

    QOLPushButtonNoUndo(text="Danger", a=wp, onclick=test)
    # sc = QOLSaveControls(a=wp)
    d = {}
    d["a"] = "astring"
    d["n"] = 7
    d["d"] = {}
    for i in range(20):
        d["d"][i] = i
    QOLDictionary(a=wp, name="d dictionary", container=d)

    jp.justpy(gui_test)
