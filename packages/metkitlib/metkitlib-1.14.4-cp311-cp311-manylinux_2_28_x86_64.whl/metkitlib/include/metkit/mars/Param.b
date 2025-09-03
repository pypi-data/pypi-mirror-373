
Param(eckit::Bless& b):
	table_(b(&table_)),
	value_(b(&value_))
{
}

Param(eckit::Evolve b):
	table_(b("Param","table_")),
	value_(b("Param","value_"))
{
}

static const char* specName()      { return "Param"; }
static void isa(TypeInfo* t)  { eckit::Isa::add(t,specName()); }
static eckit::Isa* isa()             { return eckit::Isa::get(specName());  }

static void schema(eckit::Schema& s)
{
	s.start(specName(),sizeof(Param));
	s.member("table_",member_size(Param,table_),member_offset(Param,table_),"long");
	s.member("value_",member_size(Param,value_),member_offset(Param,value_),"long");
	s.end(specName());
}


void describe(std::ostream& s,int depth = 0) const {
	eckit::_startClass(s,depth,specName());
	eckit::_describe(s,depth+1,"table_",table_);
	eckit::_describe(s,depth+1,"value_",value_);
	eckit::_endClass(s,depth,specName());
}



void _export(eckit::Exporter& h) const {
	eckit::_startClass(h,"Param");
	eckit::_export(h,"table_",table_);
	eckit::_export(h,"value_",value_);
	eckit::_endClass(h,"Param");
}


