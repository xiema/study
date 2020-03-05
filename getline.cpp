#include <iostream>
#include <string>
using namespace std;

int main () {
  string s1,s2;
  cout << "1: ";
  getline(cin, s1);
  cout << "2: ";
  getline(cin, s2);
  cout << s1 << " : " << s2;
  return 0;
}
