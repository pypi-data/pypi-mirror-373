def fact(num):
      if num < 0:
          print("Error: Factorial is not defined for negative numbers.")
      else:
          fact = 1
          for i in range(1, num + 1):
              fact *= i
          print("Factorial:", fact)

