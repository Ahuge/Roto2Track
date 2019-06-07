import nuke


class Roto2TrackGlobals(object):
    TRACKER_COLUMN_COUNT = 31
    BASE_NAME = "track 1"
    X_POS = 2
    Y_POS = 3
    T = 6
    R = 7
    S = 8


class RotoPoint(object):
    def __init__(self, point):
        super(RotoPoint, self).__init__()
        self._point = point
        print(dir(point))

    @property
    def frames(self):
        return self._point.center.getControlPointKeyTimes()

    @property
    def isKeyed(self):
        return nuke.frame() in self.frames

    @property
    def value(self):
        return self._point.center.getPosition(nuke.frame())

    def valueAt(self, frame):
        return self._point.center.getPosition(frame)


class RotoShape(object):
    def __init__(self, shape):
        super(RotoShape, self).__init__()
        self._shape = shape

    @property
    def name(self):
        return self._shape.name

    @property
    def points(self):
        for point in self._shape:
            yield RotoPoint(point)

    def toTracker(self):
        t = nuke.createNode("Tracker4")
        t.setName(self.name)
        tracks = t["tracks"]
        for index, point in enumerate(self.points):
            t["add_track"].execute()
            for frame in point.frames:
                val_x, val_y, other = point.valueAt(frame)
                tracks.setValueAt(val_x, frame, Roto2TrackGlobals.TRACKER_COLUMN_COUNT * index + Roto2TrackGlobals.X_POS)
                tracks.setValueAt(val_y, frame, Roto2TrackGlobals.TRACKER_COLUMN_COUNT * index + Roto2TrackGlobals.Y_POS)
                tracks.setValueAt(True, frame, Roto2TrackGlobals.TRACKER_COLUMN_COUNT * index + Roto2TrackGlobals.T)
                tracks.setValueAt(True, frame, Roto2TrackGlobals.TRACKER_COLUMN_COUNT * index + Roto2TrackGlobals.R)
                tracks.setValueAt(True, frame, Roto2TrackGlobals.TRACKER_COLUMN_COUNT * index + Roto2TrackGlobals.S)
            tracks.fromScript(tracks.toScript().replace(Roto2TrackGlobals.BASE_NAME, "Point%d" % index))
        return t


def get_shapes(layer):
    for child in layer:
        if isinstance(child, type(layer)):
            for shape in get_shapes(child):
                yield shape
        else:
            yield RotoShape(child)


def fromSelected():
    roto = nuke.selectedNode()
    shapes = get_shapes(roto["curves"].rootLayer)
    for shape in shapes:
        tracker = shape.toTracker()

