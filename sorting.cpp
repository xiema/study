#include <iostream>
#include <ctime>
#include <cstdlib>
using namespace std;

void swap(int* a, int* b)
{
	int t = *a;
	*a = *b;
	*b = t;
}

int partition(int arr[], int start, int end)
{
	int pivot = arr[end];
	int index = start;
	for (int i = start; i < end; i++)
	{
		if (arr[i] < pivot)
		{
			swap(&arr[i], &arr[index]);
			index++;
		}
	}
	swap(&arr[end], &arr[index]);
	return index;
}

void quicksort(int arr[], int start, int end)
{
	if (start < end)
	{
		int p = partition(arr, start, end);
		quicksort(arr, start, p-1);
		quicksort(arr, p+1, end);
	}
}

void merge(int arr[], int start, int mid, int end)
{
	int start2 = mid + 1;
	if (arr[mid] >= arr[start2])
	{
		while (start <= mid && start2 <= end)
		{
			if (arr[start] <= arr[start2])
			{
				start++;
			}
			else
			{
				int temp = arr[start2];
				for (int i=start2; i>start; i--)
				{
					arr[i] = arr[i-1];
				}
				arr[start] = temp;
				
				start++;
				mid++;
				start2++;
			}
		}
	}
}

void mergesort(int arr[], int start, int end)
{
	if (start < end)
	{
		int mid = start + (end-start)/2;
		mergesort(arr, start, mid);
		mergesort(arr, mid+1, end);
		merge(arr, start, mid, end);
	}
}

void arr_fillint(int arr[], int size);
void arr_print(int arr[], int size);

int main()
{
	int size = 10;
	int arr[size];
	arr_fillint(arr, size);
	arr_print(arr, size);
	//quicksort(arr, 0, size-1);
	mergesort(arr, 0, size-1);
	arr_print(arr, size);
	return 0;
}

//UTILITY

void arr_fillint(int arr[], int size)
{
	srand(time(NULL));
	for (int i=0; i < size; i++)
	{
		arr[i] = rand() % 1000;
	}
}

void arr_print(int arr[], int size)
{
	for (int i=0; i < size; i++)
	{
		cout << arr[i] << ' ';
	}
	cout << endl;
}