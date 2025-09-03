
StepRange(eckit::Bless& b):
	from_(b(&from_)),
	to_(b(&to_))
{
}

StepRange(eckit::Evolve b):
	from_(b("StepRange","from_")),
	to_(b("StepRange","to_"))
{
}

static const char* specName()      { return "StepRange"; }
static void isa(TypeInfo* t)  { eckit::Isa::add(t,specName()); }
static eckit::Isa* isa()             { return eckit::Isa::get(specName());  }

static void schema(eckit::Schema& s)
{
	s.start(specName(),sizeof(StepRange));
	s.member("from_",member_size(StepRange,from_),member_offset(StepRange,from_),"double");
	s.member("to_",member_size(StepRange,to_),member_offset(StepRange,to_),"double");
	s.end(specName());
}


void describe(std::ostream& s,int depth = 0) const {
	eckit::_startClass(s,depth,specName());
	eckit::_describe(s,depth+1,"from_",from_);
	eckit::_describe(s,depth+1,"to_",to_);
	eckit::_endClass(s,depth,specName());
}



void _export(eckit::Exporter& h) const {
	eckit::_startClass(h,"StepRange");
	eckit::_export(h,"from_",from_);
	eckit::_export(h,"to_",to_);
	eckit::_endClass(h,"StepRange");
}


