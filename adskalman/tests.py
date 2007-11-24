import unittest
import adskalman
import numpy
import scipy.io

def assert_3d_vs_kpm_close(A,B):
    """compare my matrices (where T dimension is first) vs. KPM's (where it's last)"""
    for i in range(A.shape[0]):
        try:
            assert numpy.allclose( A[i,:,:], B[:,:,i])
        except:
            print
            print i
            print 'A[i],',A[i]
            print "B[:,:,i]",B[:,:,i]
            raise

class TestKalman(unittest.TestCase):
    def test_kalman1(self,time_steps=100,Qsigma=0.1,Rsigma=0.5):
        dt = 0.1
        # process model
        A = numpy.array([[1, 0, dt, 0],
                         [0, 1, 0, dt],
                         [0, 0, 1,  0],
                         [0, 0, 0,  1]],
                        dtype=numpy.float64)
        # observation model
        C = numpy.array([[1, 0, 0, 0],
                         [0, 1, 0, 0]],
                        dtype=numpy.float64)
        # process covariance
        Q = Qsigma*numpy.eye(4)
        # measurement covariance
        R = Rsigma*numpy.eye(2)

        x = numpy.array([0,0,0,0])
        x += Qsigma*numpy.random.standard_normal(x.shape)

        kf = adskalman.KalmanFilter(A,C,Q,R,x,Q)
        y = numpy.dot(C,x)
        y += Rsigma*numpy.random.standard_normal(y.shape)

        xs = []
        xhats = []
        for i in range(time_steps):
            if i==0: isinitial=True
            else: isinitial = False

            xhat,P = kf.step(y=y, isinitial=isinitial)

            # calculate new state
            x = numpy.dot(A,x) + Qsigma*numpy.random.standard_normal(x.shape)
            # and new observation
            y = numpy.dot(C,x) + Rsigma*numpy.random.standard_normal(y.shape)

            xs.append(x)
            xhats.append( xhat )
        xs = numpy.array(xs)
        xhats = numpy.array(xhats)
        # XXX some comparison between xs and xhats

    def test_filt_KPM(self):
        kpm=scipy.io.loadmat('kpm_results')
        # process model
        A = numpy.array([[1, 0, 1, 0],
                         [0, 1, 0, 1],
                         [0, 0, 1,  0],
                         [0, 0, 0,  1]],
                        dtype=numpy.float64)
        # observation model
        C = numpy.array([[1, 0, 0, 0],
                         [0, 1, 0, 0]],
                        dtype=numpy.float64)
        ss=4; os=2
        # process covariance
        Q = 0.1*numpy.eye(ss)
        # measurement covariance
        R = 1.0*numpy.eye(os)
        initx = numpy.array([10, 10, 1, 0],dtype=numpy.float64)
        initV = 10.0*numpy.eye(ss)

        x = kpm['x'].T
        y = kpm['y'].T

        xfilt, Vfilt = adskalman.kalman_filter(y, A, C, Q, R, initx, initV)
        assert numpy.allclose(xfilt.T,kpm['xfilt'])
        assert_3d_vs_kpm_close(Vfilt,kpm['Vfilt'])

        xsmooth, Vsmooth = adskalman.kalman_smoother(y,A,C,Q,R,initx,initV)
        assert numpy.allclose(xsmooth.T,kpm['xsmooth'])
        assert_3d_vs_kpm_close(Vsmooth,kpm['Vsmooth'])

    def test_filt_KPM_loglik(self):
        kpm=scipy.io.loadmat('kpm_results')
        # process model
        A = numpy.array([[1, 0, 1, 0],
                         [0, 1, 0, 1],
                         [0, 0, 1,  0],
                         [0, 0, 0,  1]],
                        dtype=numpy.float64)
        # observation model
        C = numpy.array([[1, 0, 0, 0],
                         [0, 1, 0, 0]],
                        dtype=numpy.float64)
        ss=4; os=2
        # process covariance
        Q = 0.1*numpy.eye(ss)
        # measurement covariance
        R = 1.0*numpy.eye(os)
        initx = numpy.array([10, 10, 1, 0],dtype=numpy.float64)
        initV = 10.0*numpy.eye(ss)

        x = kpm['x'].T
        y = kpm['y'].T

        xfilt, Vfilt, VVfilt, loglik = adskalman.kalman_filter(y, A, C, Q, R, initx, initV,
                                                               full_output=True)
        assert numpy.allclose(xfilt.T,kpm['xfilt'])
        assert numpy.allclose(Vfilt.T,kpm['Vfilt'])
        assert_3d_vs_kpm_close(Vfilt,kpm['Vfilt'])
        assert_3d_vs_kpm_close(VVfilt,kpm['VVfilt'])
        assert numpy.allclose(loglik.T,kpm['loglik'])

        xsmooth, Vsmooth, VVsmooth, loglik = adskalman.kalman_smoother(y,A,C,Q,R,initx,initV,
                                                                       full_output=True)
        assert numpy.allclose(xsmooth.T,kpm['xsmooth'])
        assert_3d_vs_kpm_close(Vsmooth,kpm['Vsmooth'])
        assert_3d_vs_kpm_close(VVsmooth,kpm['VVsmooth'])
        assert numpy.allclose(loglik.T,kpm['loglik_smooth'])

def get_test_suite():
    ts=unittest.TestSuite([unittest.makeSuite(TestKalman),
                           ])
    return ts

if __name__=='__main__':
    unittest.main()