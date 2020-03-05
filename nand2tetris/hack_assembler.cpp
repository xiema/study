#include <fstream>
#include <iostream>
#include <cstdio>
#include <string>
#include <vector>
using namespace std;

struct ParseError : public exception {
  const char* what () const throw () {
    return "Parse error";
  }
};

class Parser {
public:
  Parser(ifstream* _fin);
  bool getline(string& line);
  bool parse();
  void display();

private:
  ifstream* fin;
  enum States
  {
    ST_DEFAULT,
    ST_COMMAND,
    ST_FRONTSLASH,
    ST_COMMENT,
  };
  vector<string> out;
  char cur_token;
  int cur_state;

  bool advance();
  bool parseAcommand();
  bool parselabel();
  bool parseCcommand();
};

Parser::Parser(ifstream* _fin)
{
  fin = _fin;
}

bool Parser::getline(string& line)
{
  if (std::getline(*fin, line))
  {
    return true;
  }
}

void Parser::display()
{
  for (vector<string>::const_iterator iter = out.begin(); iter != out.end(); ++iter) {
    cout << *iter << endl;
  }
}

bool Parser::parse()
{
  try {
    //build symbol table

    fin->seekg(0);
    //parse
    cur_state = ST_DEFAULT;
    while (advance()) {
      switch (cur_token) {
        case '@':
          parseAcommand();
          break;
        case '(':
          parselabel();
          break;
        default:
          parseCcommand();
      }
    }
  } catch(ParseError) {
    return false;
  }
  return true;
}

bool Parser::advance()
{
  while (fin->get(cur_token)) {
    switch (cur_state) {
      case ST_DEFAULT:
        if (cur_token == '/')
        {
          cur_state = ST_FRONTSLASH;
        } else if (!isspace(cur_token))
        {
          cur_state = ST_COMMAND;
          return true;
        }
        break;

      case ST_COMMAND:
        if (cur_token == '\n' or !isspace(cur_token))
        {
          cur_state = ST_DEFAULT;
          return true;
        }
        break;

      case ST_FRONTSLASH:
        if (cur_token == '/')
        {
          cur_state = ST_COMMENT;
        } else
        {
          throw ParseError();
        }
        break;

      case ST_COMMENT:
        if (cur_token == '\n')
        {
          cur_state = ST_DEFAULT;
        }
        break;
    }
  }
}

bool Parser::parseAcommand() {
  string s;
  while (advance()) {
    if (isdigit(cur_token)) {
      s += cur_token;
    } else if (cur_token == '\n') {
      out.push_back(s);
      return true;
    }
  }
}
bool Parser::parselabel() {

}
bool Parser::parseCcommand() {
  string s;
  int destflg = 0;
  while (true) {
    switch (cur_token) {
      case 'D':
      case 'M':
      case '=':
    }
  }
}




int main(int argc, char *argv[])
{
  //get filename
  string* fn;
  if (argc > 1)
  {
    fn = new string(argv[1]);
  } else
  {
    cout << "Input Filename: ";
    fn = new string;
    cin >> *fn;
  }
  //cout << fn << endl;

  //get filestream
  ifstream fin(*fn);
  if (!fin.is_open())
  {
    cout << "File not found." << endl;
    return 1;
  }


  //create new parser object
  Parser parser(&fin);

  //create symbol table vector


  //run parser
  parser.parse();
  parser.display();

  //get object code
  //write object code to file

  //clean up
  delete fn;
  return 0;
}
