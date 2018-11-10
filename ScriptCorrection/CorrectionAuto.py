import os
import re
import signal
import sys
import unittest
from subprocess import PIPE, Popen
from time import sleep


class CorrectionTp1Critere3(unittest.TestCase):
    def __init__(self, testname, arg):
        super(CorrectionTp1Critere3, self).__init__(testname)
        self._arg = arg

    def setUp(self):
        # self.PATH = PATH
        assert len(sys.argv) == 3, "Give correction AND student script"
        self.tests = []
        self.reSymValDate = re.compile(
            r"(?:[a-z]+)\([a-z]+, [0-9]{4}-[0-9]{2}-[0-9]{2}, [0-9]{4}-[0-9]{2}-[0-9]{2}\)")
        self.reDateVal = re.compile(
            r"\[((?:\(\'[0-9]{4}-[0-9]{2}-[0-9]{2}', \'[0-9]+.?[0-9]+'\)(?:, )?)+)*\]")

    def get_reponse(self, args):
        arg = ["python", sys.argv[2]] + args.split(" ")
        proc = Popen(arg, stdout=PIPE, stderr=PIPE, encoding='utf-8')
        result, err = proc.communicate(timeout=70)
        result = result.split("\n")[:-1]
        # proc = subprocess.run(arg, encoding='utf-8', stdout=PIPE)
        # result, err = proc.stdout.split("\n")[:-1], proc.stderr
        count = 0
        while len(result) <= 1 and count < 2:
            # print("Api en attente")
            proc.kill()
            sleep(60.0)
            # print("Check Api")
            proc = Popen(arg, stdout=PIPE, stderr=PIPE, encoding='utf-8')
            result, err = proc.communicate()
            result = result.split("\n")[:-1]

            # proc = subprocess.run(arg, stdout=PIPE, stderr=PIPE)
            # result, err = proc.stdout.split("\n")[:-1], proc.stderr
            count += 1
        return (result, err)

    def get_true_reponse(self, args):
        trueArg = ["python", sys.argv[1]] + args.split(" ")
        trueProc = Popen(trueArg, stdout=PIPE, stderr=PIPE, encoding='utf-8')
        trueResult, trueErr = trueProc.communicate(timeout=70)
        trueResult = trueResult.split("\n")[:-1]

        # proc = subprocess.run(arg, encoding='utf-8', stdout=PIPE)
        # result, err = proc.stdout.split("\n")[:-1], proc.stderr
        # timer = Timer(timeout_sec, proc.kill)
        # try:
        #    timer.start()
        #    stdout, stderr = proc.communicate()
        # finally:
        #    timer.cancel()
        count = 0
        while len(trueResult) <= 1 and count < 2:
            # print("\nApi en attente")
            trueProc.kill()
            sleep(60.0)
            # print("Check Api")
            trueProc = Popen(trueArg, stdout=PIPE,
                             stderr=PIPE, encoding='utf-8')
            trueResult, trueErr = trueProc.communicate()
            trueResult = trueResult.split("\n")[:-1]

            # proc = subprocess.run(arg, stdout=PIPE, stderr=PIPE)
            # result, err = proc.stdout.split("\n")[:-1], proc.stderr
            count += 1
        return (trueResult, trueErr)

    def test_formatDateVal(self):
        param = "-v=volume -d=2018-09-21 -f=2018-09-24 goog"
        reponse, err = self.get_reponse(param)
        truereponse, trueErr = self.get_true_reponse(param)
        print("\nRéponse de l'élève :\n", reponse)
        print("Réponse Attendue :\n", truereponse)
        print("Erreur de l'élève :\n", err)
        print("Erreur Attendue :\n", trueErr)
        self.assertTrue(self.reDateVal.match(reponse[1]))

    def test_params(self):
        print("\narg:", self._arg)
        print("\narg : ", self._arg, file=sys.stderr)
        param = self._arg
        reponse, err = self.get_reponse(param)
        truereponse, trueErr = self.get_true_reponse(param)
        print("Réponse de l'élève :\n", reponse)
        print("Réponse Attendue :\n", truereponse)
        print("Erreur de l'élève :\n", err)
        print("Erreur Attendue :\n", trueErr)
        self.assertTrue(self.reSymValDate.match(reponse[0]))
        self.assertTrue(self.reDateVal.match(reponse[1]))
        self.assertTrue(reponse[0] == truereponse[0])
        self.assertTrue(reponse[1][0:len(truereponse[1])] == truereponse[1][
            0:len(truereponse[1])])


try:
    with open("./params.txt") as f:
        comment = re.compile("#.+")
        params = f.readlines()
    params = [x.strip() for x in params if not comment.match(x)]
except FileNotFoundError:
    print("Veuillez mettre un fichier param.txt dans le dossier du script !")
    print("Fichier non trouvé ! Veuillez mettre un fichier param.txt dans le \
          dossier du script !", file=sys.stderr)

testFonctionement = unittest.TestSuite()
testFonctionement.addTest(CorrectionTp1Critere3('test_formatDateVal', None))
checkFonctionement = unittest.TextTestRunner(
    verbosity=2).run(testFonctionement)
if checkFonctionement.wasSuccessful():
    allTest = unittest.TestSuite()
    for param in params:
        allTest.addTest(CorrectionTp1Critere3('test_params', param))
    unittest.TextTestRunner(verbosity=2).run(allTest)
else:
    print("\nLe premier test à échoué,\nIl y à peut-être une boucle infinie\
            ou une erreur d'implémentation sur le fonctionement basique.\
            \n Code à vérifier manuellement", file=sys.stderr)
    parent_id = os.getpid()
    ps_command = Popen("ps -o pid --ppid %d --noheaders" %
                       parent_id, shell=True, stdout=PIPE, encoding='utf-8')
    ps_output = ps_command.stdout.read()
    # retcode = ps_command.wait()
    for pid_str in ps_output.strip().split("\n")[:-1]:
        os.kill(int(pid_str), signal.SIGTERM)
    sys.exit()
