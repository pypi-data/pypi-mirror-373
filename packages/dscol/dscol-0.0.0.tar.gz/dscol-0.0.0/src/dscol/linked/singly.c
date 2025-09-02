#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include "mod_linked.h"

struct NodeSingle {
    PyObject_HEAD

    PyObject *val;
    PyObject *next;
};
typedef struct NodeSingle NodeSingle;

static PyObject *
NodeSingle_New(PyTypeObject *type, PyObject *args, PyObject *kw)
{
    NodeSingle *self = (NodeSingle *)type->tp_alloc(type, 0);
    if (!self) return NULL;

    /* initialize fields to safe values so dealloc can run safely
       even if __init__ fails later */
    self->val = Py_None;
    Py_INCREF(Py_None);
    self->next = Py_None;
    Py_INCREF(Py_None);

    return (PyObject *)self;
}

static int NodeSingle_Init(NodeSingle *self, PyObject *args, PyObject *kw) {
    PyObject *val = NULL;
    PyObject *next = Py_None;
    static char *keywords[] = {"val", "next", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kw, "O|O", keywords, &val, &next)) {
        return -1;
    }
    if (next != Py_None && !PyObject_TypeCheck(next, &NodeSingleType)) {
        PyErr_SetString(PyExc_TypeError, "Expected (1)`next` to be None or NodeSingle");
        return -1;
    }
    Py_INCREF(val);
    Py_INCREF(next);
    Py_DECREF(self->val);
    Py_DECREF(self->next);
    self->val = val;
    self->next = next;
    return 0;
}

static void NodeSingle_Dealloc(NodeSingle *self) {
    Py_DECREF(self->next);
    Py_DECREF(self->val);
    Py_TYPE(self)->tp_free((PyObject *)self);
}


static PyObject *NodeSingle_get_val(NodeSingle *self, void *closure) {
    Py_INCREF(self->val);
    return self->val;
}
static PyObject *NodeSingle_get_next(NodeSingle *self, void *closure) {
    Py_INCREF(self->next);
    return self->next;
}

static int NodeSingle_set_val(NodeSingle *self, PyObject *val, void *closure) {
    Py_INCREF(val);
    Py_DECREF(self->val);
    self->val = val;
    return 0;
}
static int NodeSingle_set_next(NodeSingle *self, PyObject *next, void *closure) {
    if (next != Py_None && !PyObject_TypeCheck(next, &NodeSingleType)) {
        PyErr_SetString(PyExc_TypeError, "Expected (0)`next` to be None or NodeSingle");
        return -1;
    }
    Py_INCREF(next);
    Py_DECREF(self->next);
    self->next = next;
    return 0;
}

static PyGetSetDef NodeSingle_getsetters[] = {
    {"val", (getter)NodeSingle_get_val, (setter)NodeSingle_set_val, NULL, NULL},
    {"next", (getter)NodeSingle_get_next, (setter)NodeSingle_set_next, NULL, NULL},
    {NULL}
};

/* RECURSION ALERT */
static PyObject *NodeSingle_Repr(NodeSingle *self) {
    return PyUnicode_FromFormat("NodeSingle(val=%R, next=%R)",
                                self->val, self->next);
}
static PyObject *NodeSingle_Str(NodeSingle *self) {
    return PyUnicode_FromFormat("[%S]>%S", self->val, self->next);
}

PyTypeObject NodeSingleType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "dscol.linked.NodeSingle",
    .tp_basicsize = sizeof(NodeSingle),
    .tp_dealloc = (destructor)NodeSingle_Dealloc,
    .tp_init = (initproc)NodeSingle_Init,
    .tp_getset = NodeSingle_getsetters,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_new = (newfunc)NodeSingle_New,
    .tp_repr = (reprfunc)NodeSingle_Repr,
    .tp_str = (reprfunc)NodeSingle_Str
};
