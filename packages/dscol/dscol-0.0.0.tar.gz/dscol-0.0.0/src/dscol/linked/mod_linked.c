#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include "mod_linked.h"

static PyMethodDef exportFunc[] = {
    // name: char*, fp: *(), callcons, docstr: char*
    {NULL,NULL,0,NULL}
};

static struct PyModuleDef moddecl = {
    PyModuleDef_HEAD_INIT,

    "dscol.linked", // modname
    NULL, // docs str
    -1, // size
    exportFunc // meds
};

PyMODINIT_FUNC
PyInit_linked(void) {
    PyObject *m;

    if (PyType_Ready(&NodeSingleType) < 0)
        return NULL;

    m = PyModule_Create(&moddecl);
    if (m == NULL)
        return NULL;

    if (PyModule_AddObject(m, "NodeSingle", (PyObject *)&NodeSingleType) < 0) {
        Py_DECREF(&NodeSingleType);
        Py_DECREF(m);
        return NULL;
    }
    return m;
}

