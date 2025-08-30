// Copyright 2025 Mohamed Gaber
//
// Partially adapted from libparse-python
//
// Copyright 2024 Efabless Corporation
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
#include <sstream>
#include <string>

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "libparse.h"

#include "stdio_filebuf.h"

namespace py = pybind11;
using namespace Yosys;

void LibertyParser::error() const
{
    std::ostringstream oss;
    oss << "Syntax error in liberty file on line " << line << ".\n";
    throw std::runtime_error(oss.str());
}

void LibertyParser::error(const std::string &str) const
{
	std::stringstream oss;
	oss << "Syntax error in liberty file on line " << line << ".\n";
	oss << "  " << str << "\n";
    throw std::runtime_error(oss.str());
}


struct PyIStream : public std::istream {
	PyIStream(FILE *f) : std::istream(&buffer_), buffer_(f) {}

	static PyIStream *make_from(const py::object &pyfile)
	{
		if (pyfile.is(py::none())) {
			throw std::runtime_error("None is not a valid input stream");
		}

		auto fd_attr = pyfile.attr("fileno");
		auto fd_obj = fd_attr();
		auto fd = fd_obj.cast<int>();
		if (fd == -1) {
			throw std::runtime_error("Failed to get file descriptor");
		}

		auto f = fdopen(fd, "r");
		if (!f) {
			throw std::runtime_error("Failed to open input stream");
		}

		return new PyIStream(f);
	}

    private:
	stdio_filebuf<char> buffer_;
};

LibertyParser *from_file(const py::object &pyfile)
{
	auto cxx_stream = PyIStream::make_from(pyfile);
	return new LibertyParser(*cxx_stream);
}


PYBIND11_MODULE(_libparse, m)
{
	m.doc() = "libparse from yosys, native component";
	py::class_<LibertyAst>(m, "LibertyAst")
	  .def(py::init())
	  .def_readonly("id", &LibertyAst::id)
	  .def_readonly("value", &LibertyAst::value)
	  .def_readonly("args", &LibertyAst::args)
	  .def_readonly("children", &LibertyAst::children)
	  .def("find", &LibertyAst::find);
	py::class_<LibertyParser>(m, "LibertyParser").def(py::init(&from_file)).def_readonly("ast", &LibertyParser::ast);
}
