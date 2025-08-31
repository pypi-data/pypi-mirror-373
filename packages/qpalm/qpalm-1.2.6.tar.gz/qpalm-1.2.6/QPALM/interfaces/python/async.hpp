#pragma once

#include <pybind11/gil.h>
namespace py = pybind11;

#include <chrono>
#include <exception>
#include <future>
#include <iostream>
#include <tuple>
using namespace std::chrono_literals;

#include "thread-checker.hpp"

namespace qpalm {

template <class Solver, class Invoker, class... CheckedArgs>
void async_solve(bool async, bool suppress_interrupt, Solver &solver, Invoker &invoke_solver,
                 CheckedArgs &...checked_args) {
    if (!async) {
        // Invoke the solver synchronously
        invoke_solver();
    } else {
        // Check that the user doesn't use the same solver/problem in multiple threads
        ThreadChecker solver_checker{solver};
        std::tuple checkers{ThreadChecker{checked_args}...};
        // Invoke the solver asynchronously
        auto done = std::async(std::launch::async, invoke_solver);
        {
            py::gil_scoped_release no_gil;
            while (done.wait_for(50ms) != std::future_status::ready) {
                py::gil_scoped_acquire gil;
                // Check if Python received a signal (e.g. Ctrl+C)
                if (PyErr_CheckSignals() != 0) {
                    // Nicely ask the solver to stop
                    solver.cancel();
                    // It should return a result soon
                    if (py::gil_scoped_release no_gil_wait;
                        done.wait_for(15s) != std::future_status::ready) {
                        // If it doesn't, we terminate the entire program,
                        // because the solver uses variables local to this
                        // function, so we cannot safely return without
                        // waiting for the solver to finish.
                        std::cerr << "QPALM solver failed to respond to cancellation request. "
                                     "Terminating ..."
                                  << std::endl;
                        std::terminate();
                    }
                    if (PyErr_Occurred()) {
                        if (PyErr_ExceptionMatches(PyExc_KeyboardInterrupt) && suppress_interrupt)
                            PyErr_Clear(); // Clear the KeyboardInterrupt exception
                        else
                            throw py::error_already_set();
                    }
                    break;
                }
            }
        }
    }
}

} // namespace qpalm
