#include <iostream>
using namespace std;
int main()
{
  int amount;
  float balance;

  cin >> amount >> balance;

  if (amount % 5 == 0 and amount <= balance)
  {
    balance -= amount + 0.5;
  }

  printf("%.2f", balance);

  return 0;
}
